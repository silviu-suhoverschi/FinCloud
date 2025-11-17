import { Database } from '@nozbe/watermelondb';
import SQLiteAdapter from '@nozbe/watermelondb/adapters/sqlite';
import schema from './schema';
import * as models from '../models';

const adapter = new SQLiteAdapter({
  schema,
  dbName: 'fincloud',
  jsi: true, // Use JSI for better performance (requires react-native >= 0.68)
  onSetUpError: (error) => {
    console.error('Database setup error:', error);
  },
});

export const database = new Database({
  adapter,
  modelClasses: [
    models.Account,
    models.Transaction,
    models.Category,
    models.Budget,
    models.PortfolioAsset,
    models.PortfolioTransaction,
  ],
});
