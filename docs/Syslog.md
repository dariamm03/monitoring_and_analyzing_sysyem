# Syslog

Протокол Syslog - стандарт отправки и регистрации сообщений о происходящих в системе событиях (то есть создания событийных журналов), использующийся в компьютерных сетях, работающих по протоколу IP. Термином «syslog» называют как ныне стандартизированный сетевой протокол syslog, так и программное обеспечение (приложение, библиотеку), которое занимается отправкой и получением системных сообщений. Сообщения могут отправляться как по UDP, так и по TCP.

Syslog имеет несколько стандартизаций:

- RFC 5424 «The Syslog Protocol» (Протокол Syslog)
- RFC 5425 «Transport Layer Security (TLS) Transport Mapping for Syslog»
- RFC 5426 «Transmission of Syslog Messages over UDP»
- RFC 5427 «Textual Conventions for Syslog Management»
- RFC 5674 «Alarms in Syslog» (Аварийные сигналы в Syslog)
- RFC 5675 «Mapping Simple Network Management Protocol (SNMP) Notifications to SYSLOG Messages»
- RFC 5848 «Signed Syslog Messages»
- RFC 6012 «Datagram Transport Layer Security (DTLS) Transport Mapping for Syslog»
....

## Отправка сообщений

В примере, на стороне NetcoreBackend для отправки syslog - сообщений сделан логгер на основе стандартного логгера ILogger (Microsoft.Extensions.Logging)
Для этого добавлены следующие классы:

- **SyslogLoggerProvider** - Провайдер для syslog-логгера.
- **SyslogLogger** - Непосредственно сам логгер. В нем реализован метод Log, который формирует syslog сообщение и отправляет его на сервер.
- **SyslogLoggerExtensions** - Расширение для LoggerFactory, добавляющее провайдер для Syslog.
- **SyslogLogLevel** - Enum с типами сообщений syslog.

Все необходимые настройки находятся в appsettings.json

Пример отправки сообщения показан в Startup

```csharp
public void Configure(IApplicationBuilder app, IWebHostEnvironment env, ILoggerFactory loggerFactory)
{
	...
	// Отправка TCP-syslog сообщения с помощью кастомного логгера.
	string syslogAddress = Configuration["Logging:SyslogSettings:Server"];
	int syslogPort = int.Parse(Configuration["Logging:SyslogSettings:Port"]);
	int facility = int.Parse(Configuration["Logging:SyslogSettings:Facility"]);
	int version = int.Parse(Configuration["Logging:SyslogSettings:Version"]);
	string appName = Configuration["Logging:SyslogSettings:AppName"];
	
	loggerFactory.AddSyslog(syslogAddress, syslogPort, facility, version, 1, appName);
	var logger = loggerFactory.CreateLogger("SyslogLogger");
	logger.Log(LogLevel.Warning, "Инициирован запуск приложения.(syslog)");
	...
}
```

Пример SysLog сообщения в формате RFC 5424

```
<165>1 2003-08-24T05:14:15.000003-07:00 192.0.2.1 myproc 8710 - - TestMessage1

<165> - приоритет, расчтывается, как 8 * Facility(код источника) + Severity(важность).
1 - Version
2003-08-24T05:14:15.000003-07:00 - Дата-Время.Тип Timestamp
192.0.2.1 - хост источника сообщения.
myproc - APP-NAME.
8710 - PROCID.
STRUCTURED-DATA - что должно идти после PROCID в данном примере нет, поэтому -
Идентификатора сообщения (MSGID) - что должен идти после STRUCTURED-DATA в данном примере нет, поэтому -
Само сообщение.
```

## Приемник сообщений

В конечном итоге логи должны попасть в Loki. Но Loki не умеет напрямую с ними работать, поэтому для приема и преобразований выступает сервис Promtail. Promtail в случае syslog работает только с TCP и по стандарту RFC 5424.
Для включения syslog-сервера в promtail необходимо написать следующую конфигурацию в .yaml

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: syslog 
    syslog: 
      listen_address: 0.0.0.0:1514 
      labels: 
        job: syslog 
    relabel_configs: 
      - source_labels: [__syslog_message_hostname] 
        target_label: host 
      - source_labels: [__syslog_message_hostname] 
        target_label: hostname 
      - source_labels: [__syslog_message_severity] 
        target_label: level 
      - source_labels: [__syslog_message_app_name] 
        target_label: application 
      - source_labels: [__syslog_message_facility] 
        target_label: facility 
      - source_labels: [__syslog_connection_hostname] 
        target_label: connection_hostname
```

В этом случае promtail будет принимать сообщение по порту 1514 и отправлять их в Loki

