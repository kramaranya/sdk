/*
 * Copyright 2018 The Kubeflow Authors
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
import { Redirect, Route, Switch, withRouter } from 'react-router-dom';
import { RouteComponentProps } from 'react-router';
import { classes, stylesheet } from 'typestyle';
import Banner, { BannerProps } from 'src/components/Banner';
import { commonCss } from 'src/Css';
import Page404 from 'src/pages/404';
import { GettingStarted } from 'src/pages/GettingStarted';
import JobList from './JobList';
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
export const RoutePrefix = {
  JOB: '/job',
};

// tslint:disable-next-line:variable-name
export const RoutePage = {
  START: '/start',
  JOBS: '/jobs',
  JOB_DETAILS: `/jobs/details/:${RouteParams.jobId}`,
};

export const RoutePageFactory = {
  jobDetails: (jobId: string) => {
    return RoutePage.JOB_DETAILS.replace(`:${RouteParams.jobId}`, jobId);
  },
};

export const ExternalLinks = {
  DOCUMENTATION: 'https://www.kubeflow.org/docs/components/',
  GITHUB: 'https://github.com/kubeflow/sdk',
  GITHUB_ISSUE: 'https://github.com/kubeflow/sdk/issues/new',
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

export interface RouterProps extends RouteComponentProps {
  configs?: RouteConfig[];
}

const DEFAULT_ROUTE = RoutePage.START;

// This component is made as a wrapper to separate toolbar state for different pages.
const RouterComponent: React.FC<RouterProps> = ({ configs, location, history }) => {
  let routes: RouteConfig[] = configs || [
    { path: RoutePage.START, Component: GettingStarted },
    { path: RoutePage.JOBS, Component: JobList },
  ];

  const route = routes.find(x => location.pathname.startsWith(x.path));

  return (
    <div className={classes(commonCss.page)}>
      <div className={classes(commonCss.flex, commonCss.flexGrow)}>
        <SideNavLayout>
          <SideNav page={location.pathname} history={history} />
        </SideNavLayout>
        <div className={classes(commonCss.flexColumn, commonCss.flexGrow)}>
          <RoutedPage route={route} routes={routes} />
        </div>
      </div>
    </div>
  );
};

class RoutedPage extends React.Component<{ route?: RouteConfig; routes: RouteConfig[] }, RouteComponentState> {
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
      toolbarProps: { actions: {}, breadcrumbs: [], pageTitle: '' },
    };
  }

  public render(): JSX.Element {
    const { bannerProps, dialogProps, snackbarProps, toolbarProps } = this.state;
    const { route, routes } = this.props;

    return (
      <div className={classes(commonCss.page, commonCss.flexColumn)}>
        <Toolbar {...toolbarProps} />
        <Banner {...bannerProps} />
        <Switch>
          <Route exact={true} path={'/'} render={() => <Redirect to={DEFAULT_ROUTE} />} />
          {routes.map((config: RouteConfig, i: number) => {
            const { path, Component, notExact } = config;
            return (
              <Route
                key={i}
                exact={!notExact}
                path={path}
                render={props => <Component {...props} {...this.childProps} />}
              />
            );
          })}
          {/* 404 */}
          {!!route && (
            <Route render={(props) => <Page404 {...props} {...this.childProps} />} />
          )}
        </Switch>

        <Dialog
          className={css.dialog}
          open={dialogProps.open!}
          onClose={() => this._handleDialogClosed()}
        >
          {dialogProps.title && <DialogTitle>{dialogProps.title}</DialogTitle>}
          <DialogContent>{dialogProps.content}</DialogContent>
          <DialogActions>
            {dialogProps.buttons && dialogProps.buttons.map((b, i) => (
              <Button key={i} onClick={() => this._handleDialogClosed(b.onClick)} color='secondary'>
                {b.text}
              </Button>
            ))}
          </DialogActions>
        </Dialog>

        <Snackbar
          autoHideDuration={snackbarProps.autoHideDuration || 5000}
          message={snackbarProps.message}
          open={snackbarProps.open || false}
          onClose={this._handleSnackbarClose.bind(this)}
        />
      </div>
    );
  }

  private _updateDialog(dialogProps: DialogProps): void {
    this.setState({ dialogProps: { ...dialogProps, open: true } });
  }

  private _updateToolbar(newToolbarProps: Partial<ToolbarProps>): void {
    const toolbarProps = { ...this.state.toolbarProps, ...newToolbarProps };
    this.setState({ toolbarProps });
  }

  private _updateBanner(bannerProps: BannerProps): void {
    this.setState({ bannerProps });
  }

  private _updateSnackbar(snackbarProps: SnackbarProps): void {
    this.setState({ snackbarProps: { ...snackbarProps, open: true } });
  }

  private _handleDialogClosed(onClick?: () => void): void {
    this.setState({ dialogProps: { open: false } });
    if (onClick) {
      onClick();
    }
  }

  private _handleSnackbarClose(): void {
    this.setState({
      snackbarProps: { ...this.state.snackbarProps, open: false },
    });
  }
}

const SideNavLayout: React.FC<{}> = ({ children }) => (
  <div id='sideNav' className={classes(commonCss.flexColumn)}>
    {children}
  </div>
);

const Router = withRouter(RouterComponent);

export default Router;
