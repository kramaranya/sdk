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

import * as React from 'react';
import { classes } from 'typestyle';
import { commonCss } from '../Css';
import { ToolbarProps } from '../components/Toolbar';

interface GettingStartedProps {
  updateToolbar: (props: Partial<ToolbarProps>) => void;
}

const PAGE_CONTENT_MD = `
# Welcome to Kubeflow SDK UI

This is the local execution interface for Kubeflow SDK.

## Getting Started

The Kubeflow Trainer UI provides a web interface for managing and monitoring your local training jobs.

### Features

- **Training Jobs Management**: Create, monitor, and manage your training jobs
- **Local Execution**: Run training jobs locally with full visibility
- **Job History**: Track your training job history and results

### Quick Start

1. Navigate to **Training Jobs** to view your current jobs
2. Create a new training job using the SDK
3. Monitor job progress and logs through the interface

### Documentation

For more information about the Kubeflow SDK, visit our [documentation](https://www.kubeflow.org/docs/components/).

### Support

If you encounter any issues or have questions:

- [GitHub Issues](https://github.com/kubeflow/sdk/issues/new)
- [Documentation](https://www.kubeflow.org/docs/components/)
`;

export const GettingStarted: React.FC<GettingStartedProps> = ({ updateToolbar }) => {
  React.useEffect(() => {
    updateToolbar({
      actions: {},
      breadcrumbs: [],
      pageTitle: 'Getting Started',
    });
  }, [updateToolbar]);

  return (
    <div className={classes(commonCss.page)} style={{ padding: 20 }}>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <div dangerouslySetInnerHTML={{ __html: convertMarkdownToHtml(PAGE_CONTENT_MD) }} />
      </div>
    </div>
  );
};

// Simple markdown to HTML converter for basic content
function convertMarkdownToHtml(markdown: string): string {
  return markdown
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(.)/gm, '<p>$1')
    .replace(/(.*)$/gm, '$1</p>')
    .replace(/<p><h/g, '<h')
    .replace(/<\/h([1-6])><\/p>/g, '</h$1>');
}
