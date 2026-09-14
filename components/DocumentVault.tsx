'use client';

import React, { useState, ChangeEvent } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Lock, Unlock, Download, FileText, AlertCircle, CheckCircle2 } from 'lucide-react';
import { encryptFile, decryptFile } from '@/lib/vault-crypto';

export default function DocumentVault(): React.JSX.Element {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [password, setPassword] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [downloadData, setDownloadData] = useState<{ url: string; fileName: string } | null>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>): void => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setErrorMessage(null);
      setSuccessMessage(null);
      setDownloadData(null);
    }
  };

  const handleEncrypt = async (): Promise<void> => {
    if (!selectedFile || !password) {
      setErrorMessage('ファイルとパスワードを入力してください。');
      return;
    }

    try {
      setIsProcessing(true);
      setErrorMessage(null);
      setSuccessMessage(null);

      const result = await encryptFile(selectedFile, password);
      const blob = new Blob([result.data], { type: 'application/octet-stream' });
      const url = URL.createObjectURL(blob);

      setDownloadData({ url, fileName: result.fileName });
      setSuccessMessage('ファイルを暗号化しました！');
    } catch (error) {
      setErrorMessage('暗号化処理中にエラーが発生しました。');
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDecrypt = async (): Promise<void> => {
    if (!selectedFile || !password) {
      setErrorMessage('ファイルとパスワードを入力してください。');
      return;
    }

    try {
      setIsProcessing(true);
      setErrorMessage(null);
      setSuccessMessage(null);

      const result = await decryptFile(selectedFile, password);
      const blob = new Blob([result.data], { type: 'application/octet-stream' });
      const url = URL.createObjectURL(blob);

      setDownloadData({ url, fileName: result.fileName });
      setSuccessMessage('ファイルの復元に成功しました！');
    } catch (error) {
      setErrorMessage('復元に失敗しました。パスワードが正しくないかファイルが破損しています。');
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl font-bold">
          <FileText className="w-6 h-6 text-primary" />
          Document & Code Vault (AES-256)
        </CardTitle>
        <CardDescription>
          MS Word, Excel, PDF, Python(.py) などの任意ファイルをクライアントサイド（ブラウザ内）で AES-256 暗号化/復元します。
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="file-upload">対象ファイルを選択</Label>
          <Input
            id="file-upload"
            type="file"
            onChange={handleFileChange}
            className="cursor-pointer"
          />
          {selectedFile && (
            <p className="text-xs text-muted-foreground mt-1">
              選択中: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="vault-password">専用暗号化パスワード</Label>
          <Input
            id="vault-password"
            type="password"
            placeholder="パスワードを入力..."
            value={password}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
          />
        </div>

        {errorMessage && (
          <div className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 rounded-md border border-destructive/20">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="flex items-center gap-2 p-3 text-sm text-emerald-600 bg-emerald-50 rounded-md border border-emerald-200">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <Button
            onClick={handleEncrypt}
            disabled={isProcessing || !selectedFile || !password}
            className="w-full flex items-center justify-center gap-2"
          >
            <Lock className="w-4 h-4" />
            ファイルを暗号化 (Lock)
          </Button>

          <Button
            onClick={handleDecrypt}
            disabled={isProcessing || !selectedFile || !password}
            variant="outline"
            className="w-full flex items-center justify-center gap-2"
          >
            <Unlock className="w-4 h-4" />
            ファイルを復元 (Unlock)
          </Button>
        </div>

        {downloadData && (
          <div className="pt-4 border-t">
            <a
              href={downloadData.url}
              download={downloadData.fileName}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 rounded-md shadow transition-colors"
            >
              <Download className="w-4 h-4" />
              {downloadData.fileName} をダウンロード
            </a>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
