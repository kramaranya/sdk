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
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import Snackbar, { SnackbarProps } from '@material-ui/core/Snackbar';
import * as React from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';
import { classes, stylesheet } from 'typestyle';
import Banner, { BannerProps } from 'src/components/Banner';
import { commonCss } from 'src/Css';
import Page404 from 'src/pages/404';
import { GettingStarted } from 'src/pages/GettingStarted';
import SideNav from './SideNav';
import Toolbar, { ToolbarProps } from './Toolbar';

export type RouteConfig = {
  path: string;
  Component: React.ComponentType<any>;
  view?: any;
  notExact?: boolean;
};

const css = stylesheet({
  dialog: {
    minWidth: 250,
  },
});

export enum QUERY_PARAMS {
  jobId = 'jobId',
  view = 'view',
}

export enum RouteParams {
  jobId = 'jid',
  ID = 'id',
}

// tslint:disable-next-line:variable-name
export const RoutePage = {
  JOBS: '/jobs',
  JOB_DETAILS: `/jobs/details/:${RouteParams.jobId}`,
  START: '/start',
};

export const RoutePageFactory = {
  jobDetails: (id: string) => {
    return RoutePage.JOB_DETAILS.replace(`:${RouteParams.jobId}`, id);
  },
};

export const ExternalLinks = {
  DOCUMENTATION: 'https://www.kubeflow.org/docs/components/training/',
  GITHUB: 'https://github.com/kubeflow/training-operator',
  GITHUB_ISSUE: 'https://github.com/kubeflow/training-operator/issues/new/choose',
};

export interface DialogProps {
  buttons?: Array<{ onClick?: () => any; text: string }>;
  content?: string;
  onClose?: () => any;
  open?: boolean;
  title?: string;
}

interface RouteComponentState {
  bannerProps: BannerProps;
  dialogProps: DialogProps;
  snackbarProps: SnackbarProps;
  toolbarProps: ToolbarProps;
}

export interface RouterProps {
  configs?: RouteConfig[];
}

const DEFAULT_ROUTE = RoutePage.START;

// Simple trainer job list component (placeholder)
const JobList: React.FC = () => (
  <div style={{ padding: 20 }}>
    <h2>Training Jobs</h2>
    <p>Local training jobs will be listed here.</p>
  </div>
);

// Simple job details component (placeholder)
const JobDetails: React.FC = () => (
  <div style={{ padding: 20 }}>
    <h2>Job Details</h2>
    <p>Training job details will be shown here.</p>
  </div>
);

const Router: React.FC<RouterProps> = ({ configs }) => {
  let routes: RouteConfig[] = configs || [
    { path: RoutePage.START, Component: GettingStarted },
    { path: RoutePage.JOBS, Component: JobList },
    { path: RoutePage.JOB_DETAILS, Component: JobDetails },
  ];

  return (
    <div className={classes(commonCss.page, css.dialog)}>
      <Route render={({ ...props }) => <RoutedPage key={props.location.pathname} {...props} />} />
    </div>
  );
};

class RoutedPage extends React.Component<{ route?: RouteConfig }, RouteComponentState> {
  private childProps = {
    updateBanner: this._updateBanner.bind(this),
    updateDialog: this._updateDialog.bind(this),
    updateSnackbar: this._updateSnackbar.bind(this),
    updateToolbar: this._updateToolbar.bind(this),
  };

  constructor(props: any) {
    super(props);

    this.state = {
      bannerProps: {},
      dialogProps: { open: false },
      snackbarProps: { autoHideDuration: 5000, open: false },
      toolbarProps: { actions: [], breadcrumbs: [], pageTitle: '' },
    };
  }

  public render(): JSX.Element {
    const { bannerProps, dialogProps, snackbarProps, toolbarProps } = this.state;

    return (
      <div className={classes(commonCss.page)}>
        <Toolbar {...toolbarProps} />
        <Banner {...bannerProps} />

        <div className={classes(commonCss.flexGrow, commonCss.page)}>
          <SideNavLayout>
            <div className={classes(commonCss.page)}>
              <Switch>
                {[
                  { path: RoutePage.START, Component: GettingStarted },
                  { path: RoutePage.JOBS, Component: JobList },
                  { path: RoutePage.JOB_DETAILS, Component: JobDetails },
                ].map((route, i) => {
                  const { path, Component } = route;
                  return (
                    <Route
                      key={i}
                      path={path}
                      exact={!route.notExact}
                      render={props => <Component {...props} {...this.childProps} />}
                    />
                  );
                })}
                <Route
                  render={() => (
                    <Redirect to={DEFAULT_ROUTE} />
                  )}
                />
              </Switch>
            </div>
          </SideNavLayout>
        </div>

        <Dialog PaperProps={{ style: { minWidth: 250 } }} open={dialogProps.open!}>
          {dialogProps.title && <DialogTitle>{dialogProps.title}</DialogTitle>}
          {dialogProps.content && <DialogContent>{dialogProps.content}</DialogContent>}
          {dialogProps.buttons && (
            <DialogActions>
              {dialogProps.buttons.map((b, i) => (
                <Button key={i} onClick={this._handleDialogClosed(b.onClick)} color='secondary'>
                  {b.text}
                </Button>
              ))}
            </DialogActions>
          )}
        </Dialog>

        <Snackbar
          autoHideDuration={snackbarProps.autoHideDuration}
          message={snackbarProps.message}
          open={snackbarProps.open}
          onClose={this._handleSnackbarClose.bind(this)}
        />
      </div>
    );
  }

  private _updateDialog(dialogProps: DialogProps): void {
    // Assuming components will want to open the dialog by defualt.
    this.setState({ dialogProps: { open: true, ...dialogProps } });
  }

  private _updateToolbar(newToolbarProps: Partial<ToolbarProps>): void {
    const toolbarProps = Object.assign(this.state.toolbarProps, newToolbarProps);
    this.setState({ toolbarProps });
  }

  private _updateBanner(bannerProps: BannerProps): void {
    this.setState({ bannerProps });
  }

  private _updateSnackbar(snackbarProps: SnackbarProps): void {
    this.setState({ snackbarProps: { ...this.state.snackbarProps, ...snackbarProps } });
  }

  private _handleDialogClosed(onClick?: () => void): void {
    return () => {
      this.setState({ dialogProps: { open: false } });
      if (onClick) {
        onClick();
      }
    };
  }

  private _handleSnackbarClose(): void {
    this.setState({
      snackbarProps: { ...this.state.snackbarProps, open: false },
    });
  }
}

const SideNavLayout: React.FC<{}> = ({ children }) => (
  <div className={commonCss.flexGrow}>
    <div className={classes(commonCss.flex)}>
      <SideNav />
      <div className={classes(commonCss.flexGrow)}>{children}</div>
    </div>
  </div>
);

export default Router; 