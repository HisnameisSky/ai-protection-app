export interface VaultEncryptParams {
  file: File;
  password: string;
}

export interface VaultDecryptParams {
  file: File;
  password: string;
}

export interface ProcessingResult {
  data: Uint8Array;
  fileName: string;
}
