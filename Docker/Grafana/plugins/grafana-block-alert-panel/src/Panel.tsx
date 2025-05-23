import React, { useEffect, useState } from 'react';
import { PanelProps, Field } from '@grafana/data';
import { getDataSourceSrv } from '@grafana/runtime';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';

interface Props extends PanelProps {}

interface ParsedLog {
  prob: number;
  session: string;
  db: string;
  sql: string;
  time: string;
}

export const BlockAlertPanel: React.FC<Props> = () => {
  const [logs, setLogs] = useState<ParsedLog[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const now = Date.now();
        const from = now - 10 * 60 * 1000;

        const lokiDs: any = await getDataSourceSrv().get('loki');

        const response = await lokiDs.query({
          targets: [
            {
              refId: 'A',
              expr: `{job="block_prediction"} |= "Probability:"`,
              queryType: 'range',
            },
          ],
          range: {
            from: new Date(from),
            to: new Date(now),
          },
          intervalMs: 1000,
          maxDataPoints: 1000,
        });

        console.log("📦 Full Loki response:", response);

        const rawFrame = response?.data?.results?.A?.frames?.[0];
        if (!rawFrame) {
          console.warn("⚠️ Нет данных в results.A.frames");
          return;
        }

        const frame = typeof rawFrame === 'string' ? JSON.parse(rawFrame) : rawFrame;

        const tsField = frame.fields.find((f: any) =>
          f.name.toLowerCase() === 'ts' || f.name.toLowerCase() === 'time'
        );
        const lineField = frame.fields.find((f: any) =>
          f.name.toLowerCase() === 'line'
        );

        if (!tsField || !lineField) {
          console.warn("⚠️ Не найдены нужные поля");
          return;
        }

        const timestamps = tsField.values?.toArray ? tsField.values.toArray() : tsField.values;
        const lines = lineField.values?.toArray ? lineField.values.toArray() : lineField.values;

        const parsed: ParsedLog[] = [];

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          const timestamp = new Date(timestamps[i]).toISOString();

          console.log(`🔍 LINE: ${line}`);
          console.log(`🔍 TIME: ${timestamp}`);

          const probMatch = line.match(/Probability:\s?([\d.]+)/);
          if (probMatch) {
            const logEntry: ParsedLog = {
              prob: parseFloat(probMatch[1]),
              session: line.match(/session=(\d+)/)?.[1] || '—',
              db: line.match(/db=([a-zA-Z0-9_]+)/)?.[1] || '—',
              sql: line.match(/SQL:\s(.+?)\s*Probability:/)?.[1]?.slice(0, 100) || '—',
              time: timestamp,
            };
            parsed.push(logEntry);
          }
        }

        console.log("✅ Parsed logs count:", parsed.length);
        console.table(parsed);

        setLogs(parsed);
      } catch (err) {
        console.error('❌ Ошибка при запросе или парсинге:', err);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '1rem', fontFamily: 'sans-serif' }}>
      <h3 style={{ marginBottom: 10 }}>📈 Риск блокировок по времени</h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={logs}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10 }}
            allowDuplicatedCategory={false}
            minTickGap={20}
            interval="preserveStartEnd"
          />
          <YAxis domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} />
          <Tooltip formatter={(v: any) => `${Math.round(v * 100)}%`} />
          <Line type="monotone" dataKey="prob" stroke="#f44" dot />
        </LineChart>
      </ResponsiveContainer>

      <h3 style={{ marginTop: 20 }}>🚨 Последние потенциальные блокировки</h3>
      <ul style={{ paddingLeft: 20 }}>
        {logs.map((log, idx) => {
          let color = 'white';
          if (log.prob > 0.8) color = '#ff4c4c';
          else if (log.prob > 0.5) color = '#ffa500';
          else color = 'lightgreen';

          return (
            <li key={idx} style={{ marginBottom: 6, color }}>
              <strong>{Math.round(log.prob * 100)}%</strong> — [{log.db}] сессия {log.session} — {log.sql}
            </li>
          );
        })}
      </ul>
    </div>
  );
};
