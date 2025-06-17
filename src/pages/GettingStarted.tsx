export const GettingStarted: React.FC<GettingStartedProps> = ({ updateToolbar }) => {
  React.useEffect(() => {
    updateToolbar({
      actions: {},
      breadcrumbs: [],
      pageTitle: 'Getting Started',
    });
  }, [updateToolbar]);

  return (
    <div className={classes(commonCss.page, padding(20, 'lr'), 'kfp-start-page')}>
      <Markdown options={OPTIONS}>{PAGE_CONTENT_MD}</Markdown>
    </div>
  );
}; 