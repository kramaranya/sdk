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
import { Link, matchPath } from 'react-router-dom';
import { classes, stylesheet } from 'typestyle';
import { color, commonCss, fontsize } from '../Css';
import { RoutePage, ExternalLinks } from './Router';

interface SideNavProps {
  page?: string;
}

const css = stylesheet({
  active: {
    backgroundColor: '#eee',
    color: color.theme,
  },
  button: {
    border: 'none',
    fontSize: fontsize.base,
    outline: 'none',
    padding: 16,
    textAlign: 'left',
  },
  chevron: {
    color: '#9aa0a6',
    marginLeft: 'auto',
    padding: '3px 0',
    transform: 'rotate(0deg)',
    transition: 'transform 0.3s',
  },
  collapsedChevron: {
    transform: 'rotate(-90deg)',
  },
  collapsedList: {
    maxHeight: 0,
    overflow: 'hidden',
  },
  inactiveChevron: {
    color: '#5f6368',
  },
  link: {
    color: color.inactive,
    display: 'block',
    fontSize: fontsize.base,
    padding: '16px 20px 16px 40px',
    textDecoration: 'none',
  },
  list: {
    maxHeight: 1000,
    overflow: 'hidden',
    transition: 'max-height 0.3s',
  },
  nav: {
    background: color.background,
    borderRight: `1px solid ${color.divider}`,
    height: '100%',
    minWidth: 220,
    paddingTop: 10,
  },
  root: {
    color: color.inactive,
    display: 'block',
    fontSize: fontsize.base,
    padding: '16px 20px',
    textDecoration: 'none',
  },
  separator: {
    border: 'none',
    borderTop: `1px solid ${color.divider}`,
    margin: '10px 20px',
  },
});

const SideNav: React.FC<SideNavProps> = ({ page }) => {
  const getActiveClassName = (path: string) => {
    return matchPath(window.location.hash.substr(1), { path }) ? css.active : '';
  };

  return (
    <nav className={css.nav}>
      <Link
        className={classes(css.root, getActiveClassName(RoutePage.START))}
        to={RoutePage.START}
      >
        Getting Started
      </Link>
      
      <hr className={css.separator} />
      
      <Link
        className={classes(css.root, getActiveClassName(RoutePage.JOBS))}
        to={RoutePage.JOBS}
      >
        Training Jobs
      </Link>

      <hr className={css.separator} />

      <div style={{ padding: '20px' }}>
        <div style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>External Links</div>
        <a
          href={ExternalLinks.DOCUMENTATION}
          target="_blank"
          rel="noopener noreferrer"
          style={{ display: 'block', fontSize: '13px', color: '#1976d2', marginBottom: '8px', textDecoration: 'none' }}
        >
          Documentation
        </a>
        <a
          href={ExternalLinks.GITHUB}
          target="_blank" 
          rel="noopener noreferrer"
          style={{ display: 'block', fontSize: '13px', color: '#1976d2', marginBottom: '8px', textDecoration: 'none' }}
        >
          GitHub
        </a>
        <a
          href={ExternalLinks.GITHUB_ISSUE}
          target="_blank"
          rel="noopener noreferrer" 
          style={{ display: 'block', fontSize: '13px', color: '#1976d2', textDecoration: 'none' }}
        >
          Report Issue
        </a>
      </div>
    </nav>
  );
};

export default SideNav; 