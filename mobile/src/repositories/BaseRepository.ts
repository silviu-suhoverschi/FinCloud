import { Model, Q, Query } from '@nozbe/watermelondb';
import { database } from '../storage/database';

/**
 * Base repository with common CRUD operations
 */
export abstract class BaseRepository<T extends Model> {
  protected tableName: string;

  constructor(tableName: string) {
    this.tableName = tableName;
  }

  /**
   * Get collection
   */
  protected getCollection() {
    return database.collections.get<T>(this.tableName);
  }

  /**
   * Get all records
   */
  async getAll(): Promise<T[]> {
    return await this.getCollection().query().fetch();
  }

  /**
   * Get by ID
   */
  async getById(id: string): Promise<T | null> {
    try {
      return await this.getCollection().find(id);
    } catch {
      return null;
    }
  }

  /**
   * Get by user ID
   */
  async getByUserId(userId: string): Promise<T[]> {
    return await this.getCollection()
      .query(Q.where('user_id', userId))
      .fetch();
  }

  /**
   * Create a new record
   */
  async create(data: Partial<T>): Promise<T> {
    return await database.write(async () => {
      return await this.getCollection().create((record: any) => {
        Object.assign(record, data);
      });
    });
  }

  /**
   * Update a record
   */
  async update(id: string, data: Partial<T>): Promise<T> {
    const record = await this.getById(id);
    if (!record) {
      throw new Error(`Record with id ${id} not found`);
    }

    return await database.write(async () => {
      return await record.update((rec: any) => {
        Object.assign(rec, data);
      });
    });
  }

  /**
   * Delete a record
   */
  async delete(id: string): Promise<void> {
    const record = await this.getById(id);
    if (!record) {
      throw new Error(`Record with id ${id} not found`);
    }

    await database.write(async () => {
      await record.markAsDeleted();
    });
  }

  /**
   * Delete all records for a user
   */
  async deleteByUserId(userId: string): Promise<void> {
    const records = await this.getByUserId(userId);
    await database.write(async () => {
      await Promise.all(records.map(record => record.markAsDeleted()));
    });
  }

  /**
   * Count records
   */
  async count(): Promise<number> {
    return await this.getCollection().query().fetchCount();
  }

  /**
   * Count records by user ID
   */
  async countByUserId(userId: string): Promise<number> {
    return await this.getCollection()
      .query(Q.where('user_id', userId))
      .fetchCount();
  }

  /**
   * Custom query
   */
  async query(queryConditions: Query<T>): Promise<T[]> {
    return await queryConditions.fetch();
  }
}
