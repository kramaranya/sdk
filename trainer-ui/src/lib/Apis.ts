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

// Build info interface
export interface BuildInfo {
  apiServerMultiUser?: boolean;
  apiServerReady?: boolean;
  buildDate?: string;
  commitHash?: string;
  commitUrl?: string;
  frontendCommitHash?: string;
  tagName?: string;
}

// Basic API utilities for trainer UI
export class Apis {
  // Get build information
  static async getBuildInfo(): Promise<BuildInfo> {
    try {
      // In a real implementation, this would make an API call
      // For now, return mock data for trainer UI
      return {
        apiServerMultiUser: false,
        apiServerReady: true,
        buildDate: new Date().toISOString(),
        commitHash: 'local-dev',
        tagName: 'trainer-ui-local',
      };
    } catch (error) {
      console.warn('Failed to get build info:', error);
      return {};
    }
  }

  // Get cluster name (for GKE metadata)
  static async getClusterName(): Promise<string | undefined> {
    try {
      // In a real implementation, this would make an API call
      // For trainer UI, this is not applicable
      return undefined;
    } catch (error) {
      console.warn('Failed to get cluster name:', error);
      return undefined;
    }
  }

  // Get project ID (for GKE metadata)
  static async getProjectId(): Promise<string | undefined> {
    try {
      // In a real implementation, this would make an API call
      // For trainer UI, this is not applicable
      return undefined;
    } catch (error) {
      console.warn('Failed to get project ID:', error);
      return undefined;
    }
  }

  // Check if tensorboard pod is ready
  static async isTensorboardPodReady(_url: string): Promise<boolean> {
    // In a real implementation, this would check the pod status
    // For trainer UI, tensorboard integration would be different
    return false;
  }
}

// Export for backward compatibility
export default Apis; 