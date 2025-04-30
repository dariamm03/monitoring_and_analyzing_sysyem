import EmberRouter from '@ember/routing/router';
import config from './config/environment';

const Router = EmberRouter.extend({
  location: config.locationType
});

Router.map(function () {
  this.route('i-i-s-flexberry-sample-logging-activity-l');
  this.route('i-i-s-flexberry-sample-logging-activity-e',
  { path: 'i-i-s-flexberry-sample-logging-activity-e/:id' });
  this.route('i-i-s-flexberry-sample-logging-activity-e.new',
  { path: 'i-i-s-flexberry-sample-logging-activity-e/new' });
  this.route('i-i-s-flexberry-sample-logging-group-l');
  this.route('i-i-s-flexberry-sample-logging-group-e',
  { path: 'i-i-s-flexberry-sample-logging-group-e/:id' });
  this.route('i-i-s-flexberry-sample-logging-group-e.new',
  { path: 'i-i-s-flexberry-sample-logging-group-e/new' });
  this.route('i-i-s-flexberry-sample-logging-student-l');
  this.route('i-i-s-flexberry-sample-logging-student-e',
  { path: 'i-i-s-flexberry-sample-logging-student-e/:id' });
  this.route('i-i-s-flexberry-sample-logging-student-e.new',
  { path: 'i-i-s-flexberry-sample-logging-student-e/new' });
});

export default Router;
