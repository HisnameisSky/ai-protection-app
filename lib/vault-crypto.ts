const ITERATIONS = 100000;
const SALT_SIZE = 16;
const IV_SIZE = 12;

/**
 * パスワードとSaltからAES-GCM鍵を誘導
 */
async function deriveKey(password: string, salt: Uint8Array): Promise<CryptoKey> {
  const encoder = new TextEncoder();
  const passwordBuffer = encoder.encode(password);

  const baseKey = await crypto.subtle.importKey(
    'raw',
    passwordBuffer,
    'PBKDF2',
    false,
    ['deriveKey']
  );

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: ITERATIONS,
      hash: 'SHA-256',
    },
    baseKey,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * ファイルをAES-256-GCMで暗号化
 */
export async function encryptFile(file: File, password: string): Promise<{ data: Uint8Array; fileName: string }> {
  const fileBuffer = await file.arrayBuffer();
  const salt = crypto.getRandomValues(new Uint8Array(SALT_SIZE));
  const iv = crypto.getRandomValues(new Uint8Array(IV_SIZE));

  const key = await deriveKey(password, salt);

  const encryptedContent = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    fileBuffer
  );

  const encryptedArray = new Uint8Array(encryptedContent);
  const resultBuffer = new Uint8Array(SALT_SIZE + IV_SIZE + encryptedArray.length);

  resultBuffer.set(salt, 0);
  resultBuffer.set(iv, SALT_SIZE);
  resultBuffer.set(encryptedArray, SALT_SIZE + IV_SIZE);

  return {
    data: resultBuffer,
    fileName: `${file.name}.enc`,
  };
}

/**
 * 暗号化されたファイルを復元
 */
export async function decryptFile(file: File, password: string): Promise<{ data: Uint8Array; fileName: string }> {
  const fileBuffer = await file.arrayBuffer();
  const fullArray = new Uint8Array(fileBuffer);

  if (fullArray.length < SALT_SIZE + IV_SIZE) {
    throw new Error('Invalid file format or corrupted payload.');
  }

  const salt = fullArray.slice(0, SALT_SIZE);
  const iv = fullArray.slice(SALT_SIZE, SALT_SIZE + IV_SIZE);
  const encryptedData = fullArray.slice(SALT_SIZE + IV_SIZE);

  const key = await deriveKey(password, salt);

  const decryptedContent = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    encryptedData
  );

  const originalName = file.name.endsWith('.enc')
    ? file.name.replace(/\.enc$/, '')
    : `decrypted_${file.name}`;

  return {
    data: new Uint8Array(decryptedContent),
    fileName: originalName,
  };
}
