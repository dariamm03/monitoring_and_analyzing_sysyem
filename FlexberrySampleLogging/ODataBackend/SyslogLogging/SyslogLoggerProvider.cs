namespace IIS.FlexberrySampleLogging.SyslogLogging
{
    using Microsoft.Extensions.Logging;
    using ICSSoft.STORMNET;
    using System;

    /// <summary>
    /// Провайдер для syslog-логгера.
    /// </summary>
    public class SyslogLoggerProvider : ILoggerProvider
    {
        private readonly string host;
        private readonly int port;

        private readonly int syslogFacility;
        private readonly int version;
        private readonly int procId;
        private readonly string appName;

        /// <summary>
        /// Initializes a new instance of the <see cref="SyslogLoggerProvider"/> class.
        /// </summary>
        /// <param name="host">Адрес серверва syslog.</param>
        /// <param name="port">Порт.</param>
        /// <param name="syslogFacility">Код источника, по нему высчитывается приоритет.</param>
        /// <param name="version">Версия.</param>
        /// <param name="procId">Идентификатор процесса.</param>
        /// <param name="appName">Имя приложения.</param>
        public SyslogLoggerProvider(
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
        /// Creates a new <see cref="ILogger"/> instance.
        /// </summary>
        /// <param name="categoryName">The category name for messages produced by the logger.</param>
        /// <returns>The instance of <see cref="ILogger"/> that was created.</returns>
        public ILogger CreateLogger(string categoryName)
        {
            LogService.LogInfo("Инициирован кастомный логгер - " + categoryName);

            return new SyslogLogger(
                this.host,
                this.port,
                this.syslogFacility,
                this.version,
                this.procId,
                this.appName);
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            // Cleanup
        }
    }
}
