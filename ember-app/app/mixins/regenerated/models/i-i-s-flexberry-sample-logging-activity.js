import Mixin from '@ember/object/mixin';
import $ from 'jquery';
import DS from 'ember-data';
import { validator } from 'ember-cp-validations';
import { attr, belongsTo, hasMany } from 'ember-flexberry-data/utils/attributes';

export let Model = Mixin.create({
  activityName: DS.attr('string'),
  avaluable: DS.attr('boolean')
});

export let ValidationRules = {
  activityName: {
    descriptionKey: 'models.i-i-s-flexberry-sample-logging-activity.validations.activityName.__caption__',
    validators: [
      validator('ds-error'),
    ],
  },
  avaluable: {
    descriptionKey: 'models.i-i-s-flexberry-sample-logging-activity.validations.avaluable.__caption__',
    validators: [
      validator('ds-error'),
    ],
  },
};

export let defineProjections = function (modelClass) {
  modelClass.defineProjection('ActivityE', 'i-i-s-flexberry-sample-logging-activity', {
    activityName: attr('Название мероприятия', { index: 0 }),
    avaluable: attr('Доступно', { index: 1 })
  });

  modelClass.defineProjection('ActivityL', 'i-i-s-flexberry-sample-logging-activity', {
    activityName: attr('Название мероприятия', { index: 0 }),
    avaluable: attr('Доступно', { index: 1 })
  });
};
