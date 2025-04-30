import Controller from '@ember/controller';
import { computed } from '@ember/object';

export default Controller.extend({
  sitemap: computed('i18n.locale', function () {
    let i18n = this.get('i18n');

    return {
      nodes: [
        {
          link: 'index',
          icon: 'home',
          caption: i18n.t('forms.application.sitemap.index.caption'),
          title: i18n.t('forms.application.sitemap.index.title'),
          children: null
        }, {
          link: null,
          icon: 'list',
          caption: i18n.t('forms.application.sitemap.flexberry-sample-logging.caption'),
          title: i18n.t('forms.application.sitemap.flexberry-sample-logging.title'),
          children: [{
            link: 'i-i-s-flexberry-sample-logging-activity-l',
            caption: i18n.t('forms.application.sitemap.flexberry-sample-logging.i-i-s-flexberry-sample-logging-activity-l.caption'),
            title: i18n.t('forms.application.sitemap.flexberry-sample-logging.i-i-s-flexberry-sample-logging-activity-l.title'),
            icon: 'tags',
            children: null
          }, {
            link: 'i-i-s-flexberry-sample-logging-student-l',
            caption: i18n.t('forms.application.sitemap.flexberry-sample-logging.i-i-s-flexberry-sample-logging-student-l.caption'),
            title: i18n.t('forms.application.sitemap.flexberry-sample-logging.i-i-s-flexberry-sample-logging-student-l.title'),
            icon: 'edit',
            children: null
          }, {
            link: 'i-i-s-flexberry-sample-logging-group-l',
            caption: i18n.t('forms.application.sitemap.flexberry-sample-logging.i-i-s-flexberry-sample-logging-group-l.caption'),
            title: i18n.t('forms.application.sitemap.flexberry-sample-logging.i-i-s-flexberry-sample-logging-group-l.title'),
            icon: 'folder',
            children: null
          }]
        }
      ]
    };
  }),
})