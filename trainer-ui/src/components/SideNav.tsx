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

import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';
import DescriptionIcon from '@material-ui/icons/Description';
import DirectionsRun from '@material-ui/icons/DirectionsRun';
import OpenInNewIcon from '@material-ui/icons/OpenInNew';
import * as React from 'react';
import { History } from 'history';
import { Link } from 'react-router-dom';
import { classes, stylesheet } from 'typestyle';
import { ExternalLinks, RoutePage } from '../components/Router';
import { commonCss, fontsize } from '../Css';
import GitHubIcon from '../icons/GitHub-Mark-120px-plus.png';

export const sideNavColors = {
  bg: '#f8fafb',
  fgActive: '#0d6de7',
  fgDefault: '#9aa0a6',
  hover: '#f1f3f4',
};

const EXPANDED_SIDE_NAV_SIZE = 220;

const css = stylesheet({
  active: {
    color: sideNavColors.fgActive + ' !important',
  },
  button: {
    $nest: {
      '&::hover': {
        backgroundColor: sideNavColors.hover,
      },
    },
    borderRadius: 0,
    color: sideNavColors.fgDefault,
    display: 'block',
    fontSize: fontsize.medium,
    fontWeight: 'bold',
    height: 44,
    marginBottom: 16,
    padding: '12px 10px 10px 26px',
    textAlign: 'left',
    textTransform: 'none',
    width: '100%',
  },
  icon: {
    height: 20,
    width: 20,
    marginRight: 20,
  },
  root: {
    background: sideNavColors.bg,
    borderRight: '1px #e8eaed solid',
    paddingTop: 15,
    width: EXPANDED_SIDE_NAV_SIZE,
    height: '100vh',
  },
  label: {
    fontSize: fontsize.base,
    letterSpacing: 0.25,
    verticalAlign: 'super',
  },
  externalLink: {
    color: sideNavColors.fgDefault,
    display: 'flex',
    alignItems: 'center',
    padding: '8px 26px',
    textDecoration: 'none',
    $nest: {
      '&:hover': {
        backgroundColor: sideNavColors.hover,
      },
    },
  },
  externalIcon: {
    height: 16,
    width: 16,
    marginRight: 8,
  },
});

interface SideNavProps {
  page: string;
  history: History;
}

const SideNav: React.FC<SideNavProps> = ({ page }) => {
  const _highlightStartButton = (currentPage: string): boolean => {
    return currentPage.startsWith(RoutePage.START);
  };

  const _highlightJobsButton = (currentPage: string): boolean => {
    return currentPage.startsWith(RoutePage.JOBS);
  };

  return (
    <div className={css.root}>
      <Tooltip title={'Getting Started'} enterDelay={300} placement={'right-start'}>
        <Link id='startBtn' to={RoutePage.START} className={commonCss.unstyled}>
          <Button
            className={classes(
              css.button,
              _highlightStartButton(page) && css.active,
            )}
          >
            <DescriptionIcon className={css.icon} />
            <span className={css.label}>Getting Started</span>
          </Button>
        </Link>
      </Tooltip>

      <Tooltip title={'Training Jobs'} enterDelay={300} placement={'right-start'}>
        <Link id='jobsBtn' to={RoutePage.JOBS} className={commonCss.unstyled}>
          <Button
            className={classes(
              css.button,
              _highlightJobsButton(page) && css.active,
            )}
          >
            <DirectionsRun className={css.icon} />
            <span className={css.label}>Training Jobs</span>
          </Button>
        </Link>
      </Tooltip>

      <div style={{ marginTop: 40 }}>
        <a
          href={ExternalLinks.DOCUMENTATION}
          className={css.externalLink}
          target="_blank"
          rel="noopener noreferrer"
        >
          <DescriptionIcon className={css.externalIcon} />
          <span className={css.label}>Documentation</span>
          <OpenInNewIcon style={{ marginLeft: 'auto', height: 12, width: 12 }} />
        </a>

        <a
          href={ExternalLinks.GITHUB}
          className={css.externalLink}
          target="_blank"
          rel="noopener noreferrer"
        >
          <img src={GitHubIcon} className={css.externalIcon} alt="GitHub" />
          <span className={css.label}>GitHub</span>
          <OpenInNewIcon style={{ marginLeft: 'auto', height: 12, width: 12 }} />
        </a>
      </div>
    </div>
  );
};

export default SideNav;
