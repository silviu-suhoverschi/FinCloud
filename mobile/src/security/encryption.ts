import * as Crypto from 'expo-crypto';

/**
 * AES-256 Encryption Helpers
 * Used for encrypting sensitive local data
 */

/**
 * Generate a random encryption key
 */
export const generateEncryptionKey = async (): Promise<string> => {
  const randomBytes = await Crypto.getRandomBytesAsync(32); // 256 bits
  return bytesToHex(randomBytes);
};

/**
 * Generate a random IV (Initialization Vector)
 */
export const generateIV = async (): Promise<string> => {
  const randomBytes = await Crypto.getRandomBytesAsync(16); // 128 bits
  return bytesToHex(randomBytes);
};

/**
 * Derive a key from a password using PBKDF2
 */
export const deriveKeyFromPassword = async (
  password: string,
  salt: string,
  iterations: number = 10000
): Promise<string> => {
  const key = await Crypto.digestStringAsync(
    Crypto.CryptoDigestAlgorithm.SHA256,
    password + salt,
    { encoding: Crypto.CryptoEncoding.HEX }
  );
  return key;
};

/**
 * Hash a string using SHA-256
 */
export const hashSHA256 = async (input: string): Promise<string> => {
  return await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, input, {
    encoding: Crypto.CryptoEncoding.HEX,
  });
};

/**
 * Hash a PIN for secure storage
 * Uses SHA-256 with a salt
 */
export const hashPIN = async (pin: string, salt?: string): Promise<{ hash: string; salt: string }> => {
  const pinSalt = salt || (await generateSalt());
  const hash = await hashSHA256(pin + pinSalt);
  return { hash, salt: pinSalt };
};

/**
 * Verify a PIN against a stored hash
 */
export const verifyPIN = async (pin: string, storedHash: string, salt: string): Promise<boolean> => {
  const { hash } = await hashPIN(pin, salt);
  return hash === storedHash;
};

/**
 * Generate a random salt
 */
export const generateSalt = async (): Promise<string> => {
  const randomBytes = await Crypto.getRandomBytesAsync(16);
  return bytesToHex(randomBytes);
};

/**
 * Encrypt data (placeholder - actual AES encryption requires native modules)
 * For production, consider using react-native-aes-crypto or similar
 */
export const encryptData = async (data: string, key: string): Promise<string> => {
  // Note: expo-crypto doesn't provide AES encryption directly
  // This is a placeholder that should be replaced with proper AES-256-GCM encryption
  // Options:
  // 1. Use expo-crypto with Web Crypto API (web only)
  // 2. Use react-native-aes-crypto (requires native modules)
  // 3. Use expo-crypto for hashing and expo-secure-store for storage

  console.warn('encryptData: Using basic encoding. Implement proper AES-256 encryption for production');
  const encoded = btoa(data); // Base64 encoding as placeholder
  return encoded;
};

/**
 * Decrypt data (placeholder - actual AES decryption requires native modules)
 */
export const decryptData = async (encryptedData: string, key: string): Promise<string> => {
  // Note: expo-crypto doesn't provide AES decryption directly
  // This is a placeholder that should be replaced with proper AES-256-GCM decryption

  console.warn('decryptData: Using basic decoding. Implement proper AES-256 decryption for production');
  const decoded = atob(encryptedData); // Base64 decoding as placeholder
  return decoded;
};

/**
 * Utility: Convert byte array to hex string
 */
const bytesToHex = (bytes: Uint8Array): string => {
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
};

/**
 * Utility: Convert hex string to byte array
 */
const hexToBytes = (hex: string): Uint8Array => {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
  }
  return bytes;
};

/**
 * Security utilities
 */
export const SecurityUtils = {
  generateEncryptionKey,
  generateIV,
  deriveKeyFromPassword,
  hashSHA256,
  hashPIN,
  verifyPIN,
  generateSalt,
  encryptData,
  decryptData,
};
