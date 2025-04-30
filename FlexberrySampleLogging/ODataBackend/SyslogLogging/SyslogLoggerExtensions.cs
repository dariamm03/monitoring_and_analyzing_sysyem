namespace IIS.FlexberrySampleLogging.SyslogLogging
{
    using Microsoft.Extensions.Logging;

    /// <summary>
    /// Расширение для LoggerFactory, добавляющее провайдер для Syslog.
    /// </summary>
    public static class SyslogLoggerExtensions
    {
        /// <summary>
        /// Преобразовать значение в SQL строку.
        /// </summary>
        /// <param name="factory">Текущая LoggerFactory.</param>
        /// <param name="host">Адрес серверва syslog.</param>
        /// <param name="port">Порт.</param>
        /// <param name="syslogFacility">Код источника, по нему высчитывается приоритет.</param>
        /// <param name="version">Версия.</param>
        /// <param name="procId">Идентификатор процесса.</param>
        /// <param name="appName">Имя приложения.</param>
        /// <returns>Провайдер для Syslog-логгера.</returns>
        public static ILoggerFactory AddSyslog(
            this ILoggerFactory factory,
            string host,
            int port,
            int syslogFacility,
            int version,
            int procId,
            string appName)
        {
            factory.AddProvider(new SyslogLoggerProvider(host, port, syslogFacility, version, procId, appName));
            return factory;
        }
    }
}
