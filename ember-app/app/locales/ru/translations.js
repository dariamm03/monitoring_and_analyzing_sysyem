import $ from 'jquery';
import EmberFlexberryTranslations from 'ember-flexberry/locales/ru/translations';

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
      'spinner-caption': 'Данные загружаются, пожалуйста подождите...'
    },
    index: {
      greeting: 'Добро пожаловать на тестовый стенд ember-flexberry!'
    },

    application: {
      header: {
        menu: {
          'sitemap-button': {
            title: 'Меню'
          },
          'user-settings-service-checkbox': {
            caption: 'Использовать сервис сохранения пользовательских настроек'
          },
          'show-menu': {
            caption: 'Показать меню'
          },
          'hide-menu': {
            caption: 'Скрыть меню'
          },
          'language-dropdown': {
            caption: 'Язык приложения',
            placeholder: 'Выберите язык'
          }
        },
        login: {
          caption: 'Вход'
        },
        logout: {
          caption: 'Выход'
        }
      },

      footer: {
        'application-name': 'Flexberry sample logging',
        'application-version': {
          caption: 'Версия аддона {{version}}',
          title: 'Это версия аддона ember-flexberry, которая сейчас используется в этом тестовом приложении ' +
          '(версия npm-пакета + хэш коммита). ' +
          'Кликните, чтобы перейти на GitHub.'
        }
      },

      sitemap: {
        'application-name': {
          caption: 'Flexberry sample logging',
          title: 'Flexberry sample logging'
        },
        'application-version': {
          caption: 'Версия аддона {{version}}',
          title: 'Это версия аддона ember-flexberry, которая сейчас используется в этом тестовом приложении ' +
          '(версия npm-пакета + хэш коммита). ' +
          'Кликните, чтобы перейти на GitHub.'
        },
        index: {
          caption: 'Главная',
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
      'save-success-message-caption': 'Сохранение завершилось успешно',
      'save-success-message': 'Объект сохранен',
      'save-error-message-caption': 'Ошибка сохранения',
      'delete-success-message-caption': 'Удаление завершилось успешно',
      'delete-success-message': 'Объект удален',
      'delete-error-message-caption': 'Ошибка удаления'
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
