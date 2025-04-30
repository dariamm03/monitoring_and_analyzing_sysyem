namespace IIS.FlexberrySampleLogging.SyslogLogging
{
    using System;
    using System.Text;
    using System.Net;
    using System.Net.Sockets;
    using Microsoft.Extensions.Logging;

    /// <summary>
    /// Кастомный логгер для отправки Syslog TCP-сообщений.
    /// </summary>
    public class SyslogLogger : ILogger
    {
        private readonly string host;
        private readonly int port;

        private readonly int syslogFacility;
        private readonly int version;
        private readonly int procId;
        private readonly string appName;

        /// <summary>
        /// Initializes a new instance of the <see cref="SyslogLogger"/> class.
        /// </summary>
        /// <param name="host">Адрес серверва syslog.</param>
        /// <param name="port">Порт.</param>
        /// <param name="syslogFacility">Код источника, по нему высчитывается приоритет.</param>
        /// <param name="version">Версия.</param>
        /// <param name="procId">Идентификатор процесса.</param>
        /// <param name="appName">Имя приложения.</param>
        public SyslogLogger(
            string host,
            int port,
            int syslogFacility,
            int version,
            int procId,
            string appName)
        {
            this.host = host;
            this.port = port;
            this.syslogFacility = syslogFacility;
            this.version = version;
            this.procId = procId;
            this.appName = appName;
        }

        /// <summary>
        /// Begins a logical operation scope.
        /// </summary>
        /// <param name="state">The identifier for the scope.</param>
        /// <typeparam name="TState">The type of the state to begin scope for.</typeparam>
        /// <returns>An <see cref="IDisposable"/> that ends the logical operation scope on dispose.</returns>
        public IDisposable BeginScope<TState>(TState state)
        {
            return null;
        }

        /// <summary>
        /// Checks if the given <paramref name="logLevel"/> is enabled.
        /// </summary>
        /// <param name="logLevel">Level to be checked.</param>
        /// <returns><c>true</c> if enabled.</returns>
        public bool IsEnabled(LogLevel logLevel)
        {
            return true;
        }

        /// <summary>
        /// Writes a log entry.
        /// </summary>
        /// <param name="logLevel">Entry will be written on this level.</param>
        /// <param name="eventId">Id of the event.</param>
        /// <param name="state">The entry to be written. Can be also an object.</param>
        /// <param name="exception">The exception related to this entry.</param>
        /// <param name="formatter">Function to create a <see cref="string"/> message of the <paramref name="state"/> and <paramref name="exception"/>.</param>
        /// <typeparam name="TState">The type of the object to be written.</typeparam>
        public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception exception, Func<TState, Exception, string> formatter)
        {
            if (!IsEnabled(logLevel))
            {
                return;
            }

            if (formatter == null)
            {
                throw new ArgumentNullException(nameof(formatter));
            }

            var message = formatter(state, exception);

            if (string.IsNullOrEmpty(message))
            {
                return;
            }

            message = $"{logLevel}: {message}";

            if (exception != null)
            {
                message += Environment.NewLine + Environment.NewLine + exception.ToString();
            }

            var syslogLevel = MapToSyslogLevel(logLevel);
            Send(syslogLevel, message);
        }

        /// <summary>
        /// Отправить сообщение на syslog-сервер.
        /// </summary>
        /// <param name="logLevel">Уровень сообщения.</param>
        /// <param name="message">Сообщение.</param>
        private void Send(SyslogLogLevel logLevel, string message)
        {
            if (string.IsNullOrWhiteSpace(host) || port <= 0)
            {
                return;
            }

            /*
             * Пример SysLog сообщения в формате RFC 5424
             * <165>1 2003-08-24T05:14:15.000003-07:00 192.0.2.1 myproc 8710 - - TestMessage1
             *
             * <165> - приоритет, расичтывается как 8 * Facility(код источника) + Severity(важность).
             * 1 - Version
             * 2003-08-24T05:14:15.000003-07:00 - Дата-Время.Тип Timestamp
             * 192.0.2.1 - хост источника сообщения.
             * myproc - APP-NAME.
             * 8710 - PROCID.
             * STRUCTURED-DATA, что должно идти после PROCID в данном примере нет, поэтому -
             * Идентификатора сообщения (MSGID), что должен идти после STRUCTURED-DATA в данном примере нет, поэтому -
             * Само сообщение.
             */

            int priority = syslogFacility * 8 + (int)logLevel;
            int versionInfo = version;
            string dateTime = DateTime.Now.ToString("yyyy'-'MM'-'dd'T'HH':'mm':'ssZ");
            string hostName = Dns.GetHostName();
            string appNameInfo = appName;
            int procIdInfo = procId;

            string logMessage = $"<{priority}>{versionInfo} {dateTime} {hostName} {appNameInfo} {procIdInfo} - - {message}";
            logMessage += Environment.NewLine;

            var bytes = Encoding.UTF8.GetBytes(logMessage);

            using (TcpClient client = new TcpClient(host, port))
            {
                NetworkStream stream = client.GetStream();
                stream.Write(bytes, 0, bytes.Length);
                stream.Close();
            }
        }

        /// <summary>
        /// Преобразовывает уровень сообщения стандартного логгера в уровень syslog.
        /// </summary>
        /// <param name="level">Уровень сообщения в стандартном логгере.</param>
        /// <returns>Уровень сообщения в протоколе syslog.</returns>
        private SyslogLogLevel MapToSyslogLevel(LogLevel level)
        {
            SyslogLogLevel syslogLevel = SyslogLogLevel.Info;

            switch (level)
            {
                case LogLevel.Debug:
                    syslogLevel = SyslogLogLevel.Debug;
                    break;
                case LogLevel.Warning:
                    syslogLevel = SyslogLogLevel.Warn;
                    break;
                case LogLevel.Error:
                    syslogLevel = SyslogLogLevel.Error;
                    break;
                case LogLevel.Critical:
                    syslogLevel = SyslogLogLevel.Critical;
                    break;
                case LogLevel.Trace:
                case LogLevel.None:
                case LogLevel.Information:
                    syslogLevel = SyslogLogLevel.Info;
                    break;
            }

            return syslogLevel;
        }
    }
}
