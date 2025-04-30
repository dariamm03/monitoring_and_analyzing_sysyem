import $ from 'jquery';
import EmberFlexberryTranslations from 'ember-flexberry/locales/en/translations';

import IISFlexberrySampleLoggingActivityLForm from './forms/i-i-s-flexberry-sample-logging-activity-l';
import IISFlexberrySampleLoggingGroupLForm from './forms/i-i-s-flexberry-sample-logging-group-l';
import IISFlexberrySampleLoggingStudentLForm from './forms/i-i-s-flexberry-sample-logging-student-l';
import IISFlexberrySampleLoggingActivityEForm from './forms/i-i-s-flexberry-sample-logging-activity-e';
import IISFlexberrySampleLoggingGroupEForm from './forms/i-i-s-flexberry-sample-logging-group-e';
import IISFlexberrySampleLoggingStudentEForm from './forms/i-i-s-flexberry-sample-logging-student-e';
import IISFlexberrySampleLoggingActivityModel from './models/i-i-s-flexberry-sample-logging-activity';
import IISFlexberrySampleLoggingGroupModel from './models/i-i-s-flexberry-sample-logging-group';
import IISFlexberrySampleLoggingStudentModel from './models/i-i-s-flexberry-sample-logging-student';

const translations = {};
$.extend(true, translations, EmberFlexberryTranslations);

$.extend(true, translations, {
  models: {
    'i-i-s-flexberry-sample-logging-activity': IISFlexberrySampleLoggingActivityModel,
    'i-i-s-flexberry-sample-logging-group': IISFlexberrySampleLoggingGroupModel,
    'i-i-s-flexberry-sample-logging-student': IISFlexberrySampleLoggingStudentModel
  },

  'application-name': 'Flexberry sample logging',

  forms: {
    loading: {
      'spinner-caption': 'Loading stuff, please wait for a moment...'
    },
    index: {
      greeting: 'Welcome to ember-flexberry test stand!'
    },

    application: {
      header: {
        menu: {
          'sitemap-button': {
            title: 'Menu'
          },
          'user-settings-service-checkbox': {
            caption: 'Use service to save user settings'
          },
          'show-menu': {
            caption: 'Show menu'
          },
          'hide-menu': {
            caption: 'Hide menu'
          },
          'language-dropdown': {
            caption: 'Application language',
            placeholder: 'Choose language'
          }
        },
        login: {
          caption: 'Login'
        },
        logout: {
          caption: 'Logout'
        }
      },

      footer: {
        'application-name': 'Flexberry sample logging',
        'application-version': {
          caption: 'Addon version {{version}}',
          title: 'It is version of ember-flexberry addon, which uses in this dummy application ' +
          '(npm version + commit sha). ' +
          'Click to open commit on GitHub.'
        }
      },

      sitemap: {
        'application-name': {
          caption: 'Flexberry sample logging',
          title: 'Flexberry sample logging'
        },
        'application-version': {
          caption: 'Addon version {{version}}',
          title: 'It is version of ember-flexberry addon, which uses in this dummy application ' +
          '(npm version + commit sha). ' +
          'Click to open commit on GitHub.'
        },
        index: {
          caption: 'Home',
          title: ''
        },
        'flexberry-sample-logging': {
          caption: 'FlexberrySampleLogging',
          title: 'FlexberrySampleLogging',
          'i-i-s-flexberry-sample-logging-activity-l': {
            caption: 'Activity',
            title: ''
          },
          'i-i-s-flexberry-sample-logging-student-l': {
            caption: 'Student',
            title: ''
          },
          'i-i-s-flexberry-sample-logging-group-l': {
            caption: 'Group',
            title: ''
          }
        }
      }
    },

    'edit-form': {
      'save-success-message-caption': 'Save operation succeed',
      'save-success-message': 'Object saved',
      'save-error-message-caption': 'Save operation failed',
      'delete-success-message-caption': 'Delete operation succeed',
      'delete-success-message': 'Object deleted',
      'delete-error-message-caption': 'Delete operation failed'
    },
    'i-i-s-flexberry-sample-logging-activity-l': IISFlexberrySampleLoggingActivityLForm,
    'i-i-s-flexberry-sample-logging-group-l': IISFlexberrySampleLoggingGroupLForm,
    'i-i-s-flexberry-sample-logging-student-l': IISFlexberrySampleLoggingStudentLForm,
    'i-i-s-flexberry-sample-logging-activity-e': IISFlexberrySampleLoggingActivityEForm,
    'i-i-s-flexberry-sample-logging-group-e': IISFlexberrySampleLoggingGroupEForm,
    'i-i-s-flexberry-sample-logging-student-e': IISFlexberrySampleLoggingStudentEForm
  },

});

export default translations;
