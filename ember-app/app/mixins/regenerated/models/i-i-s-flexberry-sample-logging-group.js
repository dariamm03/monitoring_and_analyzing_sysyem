import Mixin from '@ember/object/mixin';
import $ from 'jquery';
import DS from 'ember-data';
import { validator } from 'ember-cp-validations';
import { attr, belongsTo, hasMany } from 'ember-flexberry-data/utils/attributes';

export let Model = Mixin.create({
  groupName: DS.attr('string')
});

export let ValidationRules = {
  groupName: {
    descriptionKey: 'models.i-i-s-flexberry-sample-logging-group.validations.groupName.__caption__',
    validators: [
      validator('ds-error'),
    ],
  },
};

export let defineProjections = function (modelClass) {
  modelClass.defineProjection('GroupE', 'i-i-s-flexberry-sample-logging-group', {
    groupName: attr('Название группы', { index: 0 })
  });

  modelClass.defineProjection('GroupL', 'i-i-s-flexberry-sample-logging-group', {
    groupName: attr('Название группы', { index: 0 })
  });
};
