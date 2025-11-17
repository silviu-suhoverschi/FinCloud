import { categoryRepository } from '../repositories';
import { mmkvStorage, StorageKeys } from '../storage/mmkv';

export interface PresetCategory {
  name: {
    en: string;
    ro: string;
  };
  type: 'income' | 'expense';
  icon: string;
  color: string;
}

const PRESET_CATEGORIES: PresetCategory[] = [
  // Income categories
  {
    name: { en: 'Salary', ro: 'Salariu' },
    type: 'income',
    icon: '💼',
    color: '#4CAF50',
  },
  {
    name: { en: 'Freelance', ro: 'Freelance' },
    type: 'income',
    icon: '💻',
    color: '#2196F3',
  },
  {
    name: { en: 'Investment', ro: 'Investiții' },
    type: 'income',
    icon: '📈',
    color: '#9C27B0',
  },
  {
    name: { en: 'Gift', ro: 'Cadou' },
    type: 'income',
    icon: '🎁',
    color: '#FF9800',
  },
  {
    name: { en: 'Other Income', ro: 'Alte Venituri' },
    type: 'income',
    icon: '💰',
    color: '#00BCD4',
  },

  // Expense categories
  {
    name: { en: 'Food & Dining', ro: 'Mâncare & Restaurant' },
    type: 'expense',
    icon: '🍽️',
    color: '#F44336',
  },
  {
    name: { en: 'Groceries', ro: 'Cumpărături' },
    type: 'expense',
    icon: '🛒',
    color: '#4CAF50',
  },
  {
    name: { en: 'Transportation', ro: 'Transport' },
    type: 'expense',
    icon: '🚗',
    color: '#2196F3',
  },
  {
    name: { en: 'Utilities', ro: 'Utilități' },
    type: 'expense',
    icon: '💡',
    color: '#FF9800',
  },
  {
    name: { en: 'Housing', ro: 'Locuință' },
    type: 'expense',
    icon: '🏠',
    color: '#795548',
  },
  {
    name: { en: 'Healthcare', ro: 'Sănătate' },
    type: 'expense',
    icon: '🏥',
    color: '#E91E63',
  },
  {
    name: { en: 'Entertainment', ro: 'Divertisment' },
    type: 'expense',
    icon: '🎬',
    color: '#9C27B0',
  },
  {
    name: { en: 'Shopping', ro: 'Cumpărături' },
    type: 'expense',
    icon: '🛍️',
    color: '#E91E63',
  },
  {
    name: { en: 'Travel', ro: 'Călătorii' },
    type: 'expense',
    icon: '✈️',
    color: '#00BCD4',
  },
  {
    name: { en: 'Education', ro: 'Educație' },
    type: 'expense',
    icon: '📚',
    color: '#3F51B5',
  },
  {
    name: { en: 'Personal Care', ro: 'Îngrijire Personală' },
    type: 'expense',
    icon: '💆',
    color: '#FF4081',
  },
  {
    name: { en: 'Insurance', ro: 'Asigurări' },
    type: 'expense',
    icon: '🛡️',
    color: '#607D8B',
  },
  {
    name: { en: 'Subscriptions', ro: 'Abonamente' },
    type: 'expense',
    icon: '📱',
    color: '#FF5722',
  },
  {
    name: { en: 'Pet Care', ro: 'Îngrijirea Animalelor' },
    type: 'expense',
    icon: '🐾',
    color: '#8BC34A',
  },
  {
    name: { en: 'Other Expenses', ro: 'Alte Cheltuieli' },
    type: 'expense',
    icon: '💸',
    color: '#9E9E9E',
  },
];

class CategorySeedService {
  private readonly SEEDED_KEY = StorageKeys.HAS_SEEDED_CATEGORIES;

  /**
   * Check if categories have been seeded
   */
  hasSeeded(): boolean {
    return mmkvStorage.getBoolean(this.SEEDED_KEY) || false;
  }

  /**
   * Mark categories as seeded
   */
  private markAsSeeded(): void {
    mmkvStorage.set(this.SEEDED_KEY, true);
  }

  /**
   * Seed preset categories for a user
   */
  async seedCategories(userId: string, language: 'en' | 'ro' = 'en'): Promise<number> {
    // Check if already seeded
    if (this.hasSeeded()) {
      console.log('Categories already seeded');
      return 0;
    }

    let seededCount = 0;

    try {
      for (const preset of PRESET_CATEGORIES) {
        await categoryRepository.create({
          userId,
          name: preset.name[language],
          type: preset.type,
          icon: preset.icon,
          color: preset.color,
          isDefault: true,
        });
        seededCount++;
      }

      this.markAsSeeded();
      console.log(`Successfully seeded ${seededCount} preset categories`);
    } catch (error) {
      console.error('Error seeding categories:', error);
      throw error;
    }

    return seededCount;
  }

  /**
   * Get all preset categories
   */
  getPresetCategories(): PresetCategory[] {
    return PRESET_CATEGORIES;
  }

  /**
   * Reset seeding status (for testing/development)
   */
  resetSeedingStatus(): void {
    mmkvStorage.delete(this.SEEDED_KEY);
  }

  /**
   * Re-seed categories with a different language
   */
  async reseedWithLanguage(
    userId: string,
    language: 'en' | 'ro'
  ): Promise<number> {
    // Delete existing default categories
    const existingCategories = await categoryRepository.getByUserId(userId);
    for (const category of existingCategories) {
      if (category.isDefault) {
        await categoryRepository.delete(category.id);
      }
    }

    // Reset seeding status
    this.resetSeedingStatus();

    // Seed with new language
    return this.seedCategories(userId, language);
  }
}

export const categorySeedService = new CategorySeedService();
export { PRESET_CATEGORIES };
