using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using System.IO;
using System.Linq;


public class ErrorSpikeDetectorService : BackgroundService
{
    private readonly ILogger<ErrorSpikeDetectorService> _logger;
    private readonly IConfiguration _config;
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly string _lokiUrl;
    private readonly string _telegramToken;
    private readonly TimeSpan _interval = TimeSpan.FromSeconds(30);

    public ErrorSpikeDetectorService(
        ILogger<ErrorSpikeDetectorService> logger,
        IConfiguration config,
        IHttpClientFactory httpClientFactory)
    {
        _logger = logger;
        _config = config;
        _httpClientFactory = httpClientFactory;
        _lokiUrl = _config["Loki:Url"] ?? "http://loki:3100";
        _telegramToken = _config["Telegram:BotToken"];
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var lastSentTimes = new Dictionary<string, DateTime>();
        var client = _httpClientFactory.CreateClient();

        var settingsDir = Path.Combine(AppContext.BaseDirectory, "../../../../../Docker/settings");
        var settingFiles = Directory.GetFiles(settingsDir, "*.json");
        _logger.LogInformation($"📁 Найдено файлов настроек: {settingFiles.Length}");

        while (!stoppingToken.IsCancellationRequested)
        {
            foreach (var file in settingFiles)
            {
                try
                {
                    var json = await File.ReadAllTextAsync(file, stoppingToken);
                    var userSettings = JsonDocument.Parse(json).RootElement;

                    if (!userSettings.TryGetProperty("log_monitoring", out var logSettings))
                        continue;

                    string chatId = Path.GetFileNameWithoutExtension(file);  // chat_id = имя файла
                    string level = logSettings.GetProperty("level").GetString().ToLower();
                    int window = logSettings.GetProperty("window_minutes").GetInt32();
                    double threshold = logSettings.GetProperty("threshold").GetDouble();
                    int interval = logSettings.GetProperty("notification_interval").GetInt32();

                    string query = $"{_lokiUrl}/loki/api/v1/query?query=count_over_time({{level=\"{level}\"}}[{window}m])";
                    var response = await client.GetStringAsync(query);
                    int count = ParseCount(response);

                    string baseQuery = $"{_lokiUrl}/loki/api/v1/query?query=count_over_time({{level=\"{level}\"}}[60m])";
                    var baseResponse = await client.GetStringAsync(baseQuery);
                    int baseCount = ParseCount(baseResponse);
                    double baseline = (double)baseCount / (60.0 / window);
                    if (baseline == 0) baseline = 1;

                    _logger.LogInformation($"🔍 chat_id={chatId}, level={level}, count={count}, baseline={baseline:F1}, threshold={threshold}");

                    if (count / baseline >= threshold)
                    {
                        if (!lastSentTimes.TryGetValue(chatId, out var lastTime) || (DateTime.UtcNow - lastTime).TotalSeconds >= interval)
                        {
                            lastSentTimes[chatId] = DateTime.UtcNow;
                            await SendTelegramAlert(chatId, level, count, baseline, threshold, window);
                        }
                        else
                        {
                            _logger.LogInformation($"⏱ Пропускаем отправку для {chatId}, не прошло {interval} секунд");
                        }
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, $"❌ Ошибка при обработке файла {file}");
                }
            }

            await Task.Delay(_interval, stoppingToken);
        }
    }

    private int ParseCount(string json)
    {
        using var doc = JsonDocument.Parse(json);
        var val = doc.RootElement.GetProperty("data").GetProperty("result");
        if (val.GetArrayLength() == 0)
            return 0;

        string countStr = val[0].GetProperty("value")[1].GetString();
        return int.TryParse(countStr.Split('.')[0], out var count) ? count : 0;
    }

    private async Task<byte[]> RenderGrafanaPanelImage(string renderUrl)
    {
        var client = _httpClientFactory.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue(
                "Basic",
                Convert.ToBase64String(System.Text.Encoding.ASCII.GetBytes("admin:admin")));

        var response = await client.GetAsync(renderUrl);
        _logger.LogInformation($"🖼 Ответ Grafana: {response.StatusCode}");
        var preview = await response.Content.ReadAsStringAsync();
        _logger.LogInformation($"🖼 Текстовый ответ Grafana (первые 500 символов): {preview.Substring(0, Math.Min(500, preview.Length))}");

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsByteArrayAsync();
    }

    private async Task SendTelegramPhoto(string chatId, byte[] imageBytes, string caption)
    {
        var url = $"https://api.telegram.org/bot{_telegramToken}/sendPhoto";

        using var content = new MultipartFormDataContent();
        content.Add(new ByteArrayContent(imageBytes), "photo", "grafana.png");
        content.Add(new StringContent(chatId), "chat_id");
        content.Add(new StringContent(caption), "caption");
        content.Add(new StringContent("Markdown"), "parse_mode");

        var client = _httpClientFactory.CreateClient();
        var response = await client.PostAsync(url, content);
        var respText = await response.Content.ReadAsStringAsync();

        _logger.LogInformation($"📷 Telegram photo sent: {response.StatusCode} - {respText}");
    }

    private string GenerateGrafanaExploreUrl(string level)
    {
        string expr = $"count_over_time({{level=\"{level}\"}} [30m])";

        var exploreState = new
        {
            datasource = "Loki",
            queries = new[]
            {
                new {
                    refId = "A",
                    expr = expr,
                    queryType = "range"
                }
            },
            range = new { from = "now-30m", to = "now" }
        };

        var options = new JsonSerializerOptions
        {
            Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
        };

        string json = JsonSerializer.Serialize(exploreState, options);
        string encoded = Uri.EscapeDataString(json);
        encoded = encoded.Replace("_", "%5F");

        return $"http://localhost:3001/explore?orgId=1&left={encoded}";
    }




   private async Task SendTelegramAlert(string chatId, string level, int count, double baseline, double threshold, int window)
    {
        string timestamp = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss") + " UTC";

        string rawQuery = $"{{level=\"{level}\"}}";
        string lokiLink = GenerateGrafanaExploreUrl(level);


        var samples = await FetchSampleLogs(level, window);

        string serviceName = "неизвестный сервис";
        if (samples.Any())
        {
            var first = samples.First();
            var match = System.Text.RegularExpressions.Regex.Match(first, @"service_name\s*=\s*(\S+)");
            if (match.Success)
                serviceName = match.Groups[1].Value.Trim('"');
        }

        string logsText = samples.Count > 0
            ? string.Join("\n", samples.Select(l => $"• {l.Split('\n')[0].Trim()}"))
            : "_Нет примеров логов._";

        string message = $"⚠️ *{serviceName}*: превышение логов уровня *{level}*\n\n" +
                $"📌 *Время:* {timestamp}\n" +
                $"📈 За последние *{window} мин*: {count} сообщений\n" +
                $"📉 В среднем за час: {baseline:F1}\n" +
                $"🚨 Порог срабатывания: превышение в x{threshold:F1}\n\n" +
                $"🧾 *Примеры:*\n{logsText}\n\n" +
                $"🔎 <a href=\"{lokiLink}\">Открыть в Grafana</a>\n" + 
                $"_Отправлено автоматически. Проверьте систему._";

        string renderUrl = $"http://localhost:3001/render/d-solo/delj0k4800cn4f/log-monitoring" +
                   $"?orgId=1&from=now-6h&to=now&panelId=1&width=1000&height=500&tz=browser";

        try
        {
            var image = await RenderGrafanaPanelImage(renderUrl);
            await SendTelegramPhoto(chatId, image, message); // 👈 передаём весь текст сюда
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Ошибка при отправке изображения Grafana в Telegram");

            // fallback на обычное текстовое сообщение, если график не отправился
            var fallbackUrl = $"https://api.telegram.org/bot{_telegramToken}/sendMessage";
            var fallbackContent = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                { "chat_id", chatId },
                { "text", message },
                { "parse_mode", "Markdown" },
                { "disable_web_page_preview", "true" }
            });

            var client = _httpClientFactory.CreateClient();
            var response = await client.PostAsync(fallbackUrl, fallbackContent);
            var respText = await response.Content.ReadAsStringAsync();

            _logger.LogInformation($"📨 Fallback Telegram message: {response.StatusCode} - {respText}");
        }

    }



    private async Task<List<string>> FetchSampleLogs(string level, int windowMinutes)
    {
        var client = _httpClientFactory.CreateClient();
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        var start = now - windowMinutes * 60 * 1000;

        string query = Uri.EscapeDataString($"{{level=\"{level}\"}}");
        string url = $"{_lokiUrl}/loki/api/v1/query_range?query={query}&start={start}000000&end={now}000000&limit=3&direction=BACKWARD";

        var response = await client.GetAsync(url);
        var content = await response.Content.ReadAsStringAsync();

        using var doc = JsonDocument.Parse(content);
        var result = doc.RootElement.GetProperty("data").GetProperty("result");

        var samples = new List<string>();
        foreach (var stream in result.EnumerateArray())
        {
            foreach (var entry in stream.GetProperty("values").EnumerateArray())
            {
                samples.Add(entry[1].GetString());
                if (samples.Count >= 3) break;
            }
            if (samples.Count >= 3) break;
        }

        return samples;
    }


    private async Task<string> GetExampleLog(string level, int minutes)
    {
        try
        {
            var query = $"{_lokiUrl}/loki/api/v1/query?query={{level=\"{level}\"}}[{minutes}m]";
            var client = _httpClientFactory.CreateClient();
            var response = await client.GetStringAsync(query);

            using var doc = JsonDocument.Parse(response);
            var results = doc.RootElement.GetProperty("data").GetProperty("result");

            if (results.GetArrayLength() > 0)
            {
                var values = results[0].GetProperty("values");
                if (values.GetArrayLength() > 0)
                {
                    return values[0][1].GetString();  // текст лога
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Ошибка при получении примера лога из Loki.");
        }

        return null;
    }

    private string Truncate(string text, int maxLength)
    {
        return text.Length > maxLength ? text.Substring(0, maxLength) + "..." : text;
    }

}
