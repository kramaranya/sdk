/*
 * Copyright 2024 The Kubeflow Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Basic logger implementation
export const logger = {
  log: (message?: any, ...optionalParams: any[]) => {
    console.log(message, ...optionalParams);
  },
  warn: (message?: any, ...optionalParams: any[]) => {
    console.warn(message, ...optionalParams);
  },
  error: (message?: any, ...optionalParams: any[]) => {
    console.error(message, ...optionalParams);
  },
  info: (message?: any, ...optionalParams: any[]) => {
    console.info(message, ...optionalParams);
  },
  debug: (message?: any, ...optionalParams: any[]) => {
    console.debug(message, ...optionalParams);
  },
  verbose: (message?: any, ...optionalParams: any[]) => {
    console.debug(message, ...optionalParams);
  },
};

// Error extension utility
export function extendError(error: any, message: string): Error {
  if (error instanceof Error) {
    error.message = `${message}: ${error.message}`;
    return error;
  }
  return new Error(`${message}: ${error}`);
}

// Generate S3 artifact URL
export function generateS3ArtifactUrl(s3Uri: string): string {
  // Parse s3://bucket/key format
  const match = s3Uri.match(/^s3:\/\/([^/]+)\/(.+)$/);
  if (!match) {
    return s3Uri; // Return original if parsing fails
  }
  const [, bucketName, key] = match;
  return `https://${bucketName}.s3.amazonaws.com/${key}`;
}

// Generate MinIO artifact URL
export function generateMinioArtifactUrl(minioUri: string): string {
  // Parse minio://endpoint/bucket/key format
  const match = minioUri.match(/^minio:\/\/([^/]+)\/([^/]+)\/(.+)$/);
  if (!match) {
    return minioUri; // Return original if parsing fails
  }
  const [, endpoint, bucketName, key] = match;
  return `http://${endpoint}/${bucketName}/${key}`;
}

// Generate GCS Console URI
export function generateGcsConsoleUri(gcsUri: string): string | undefined {
  // Parse gs://bucket/key format
  const match = gcsUri.match(/^gs:\/\/([^/]+)\/(.+)$/);
  if (!match) {
    return undefined; // Return undefined if parsing fails
  }
  const [, bucketName, key] = match;
  return `https://console.cloud.google.com/storage/browser/${bucketName}/${key}`;
}

// URL safe string utility
export function urlSafe(str: string): string {
  return encodeURIComponent(str);
}

// Safe JSON parse
export function safeJsonParse(jsonString: string, defaultValue: any = null): any {
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    logger.warn('Failed to parse JSON:', error);
    return defaultValue;
  }
}

// Format date utility
export function formatDate(date: Date | string | number): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return 'Invalid Date';
  }
  return d.toLocaleString();
}

// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

// Deep clone utility
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T;
  }
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }
  if (typeof obj === 'object') {
    const clonedObj = {} as { [key: string]: any };
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        clonedObj[key] = deepClone((obj as { [key: string]: any })[key]);
      }
    }
    return clonedObj as T;
  }
  return obj;
} 