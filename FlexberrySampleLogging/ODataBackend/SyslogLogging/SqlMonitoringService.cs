using System;
using System.Data.SqlClient;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection; // <-- добавлено для Startup

public class SqlMonitoringService : BackgroundService
{
    private readonly ILogger<SqlMonitoringService> _logger;
    private readonly string _connectionString;
    private readonly TimeSpan _interval = TimeSpan.FromMinutes(5);

    public SqlMonitoringService(ILogger<SqlMonitoringService> logger, IConfiguration config)
    {
        _logger = logger;
        _connectionString = config.GetSection("SqlMonitoring")?["ConnectionString"];
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
{
    _logger.LogWarning("[SQL_MONITOR] ПРОВЕРКА ПОДКЛЮЧЕНИЯ: сервис запущен");

    try
    {
        using (SqlConnection conn = new SqlConnection(_connectionString))
        {
            await conn.OpenAsync(stoppingToken);
            _logger.LogWarning("[SQL_MONITOR] ПОДКЛЮЧЕНИЕ К БД УСПЕШНО");
        }
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "[SQL_MONITOR] НЕ УДАЛОСЬ ПОДКЛЮЧИТЬСЯ К SQL SERVER");
    }
        _logger.LogInformation("SQL мониторинг блокировок запущен.");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using (SqlConnection conn = new SqlConnection(_connectionString))
                {
                    await conn.OpenAsync(stoppingToken);

                    string query = @"
                        SELECT r.blocking_session_id, r.session_id, r.wait_type, r.wait_time, 
                               l.resource_type, DB_NAME(r.database_id), st.text
                        FROM sys.dm_exec_requests r
                        JOIN sys.dm_tran_locks l ON r.session_id = l.request_session_id
                        OUTER APPLY sys.dm_exec_sql_text(r.sql_handle) AS st
                        WHERE r.blocking_session_id IS NOT NULL";

                    using (SqlCommand cmd = new SqlCommand(query, conn))
                    using (SqlDataReader reader = await cmd.ExecuteReaderAsync(stoppingToken))
                    {
                        while (await reader.ReadAsync(stoppingToken))
                        {
                            string msg = $"[SQL_MONITOR] blocking_session={reader[0]}, blocked_session={reader[1]}, wait_type={reader[2]}, wait_time_ms={reader[3]}, resource={reader[4]}, db={reader[5]}, query=\"{reader[6]?.ToString()?.Replace("\n", " ")?.Replace("\r", " ")}";
                            _logger.LogWarning(msg);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при мониторинге SQL блокировок.");
            }

            await Task.Delay(_interval, stoppingToken);
        }
    }
}

