import React, { useEffect, useState } from 'react';
import { PanelProps } from '@grafana/data';

interface LogEntry {
  timestamp: string;
  user: string;
  app: string;
  message: string;
  probability: number;
}

export const Panel: React.FC<PanelProps> = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
  
    useEffect(() => {
      fetch('/public/logs.json')
        .then((res) => res.json())
        .then(setLogs)
        .catch(console.error);
    }, []);
  
    return (
      <div style={{ padding: '10px' }}>
        <h3>🔍 ML-предсказания по логам</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#eee' }}>
              <th>🕒 Время</th>
              <th>👤 Пользователь</th>
              <th>🧩 Программа</th>
              <th>💬 Сообщение</th>
              <th>🎯 Вероятность</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, i) => (
              <tr
                key={i}
                style={{
                  backgroundColor: log.probability > 0.9 ? '#ffebeb' : 'transparent',
                }}
              >
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td>{log.user}</td>
                <td>{log.app}</td>
                <td>{log.message}</td>
                <td>{(log.probability * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };
  
