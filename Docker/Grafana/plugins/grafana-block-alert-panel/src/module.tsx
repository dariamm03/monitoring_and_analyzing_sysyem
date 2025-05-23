import { PanelPlugin } from '@grafana/data';
import { BlockAlertPanel } from './Panel';

export const plugin = new PanelPlugin(BlockAlertPanel);
