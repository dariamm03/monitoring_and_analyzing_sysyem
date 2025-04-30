import Mixin from '@ember/object/mixin';
import $ from 'jquery';
import DS from 'ember-data';
import { validator } from 'ember-cp-validations';
import { attr, belongsTo, hasMany } from 'ember-flexberry-data/utils/attributes';

export let Model = Mixin.create({
  age: DS.attr('number'),
  sex: DS.attr('string'),
  studentName: DS.attr('string'),
  group: DS.belongsTo('i-i-s-flexberry-sample-logging-group', { inverse: null, async: false })
});

export let ValidationRules = {
  age: {
    descriptionKey: 'models.i-i-s-flexberry-sample-logging-student.validations.age.__caption__',
    validators: [
      validator('ds-error'),
      validator('number', { allowString: true, allowBlank: true, integer: true }),
    ],
  },
  sex: {
    descriptionKey: 'models.i-i-s-flexberry-sample-logging-student.validations.sex.__caption__',
    validators: [
      validator('ds-error'),
    ],
  },
  studentName: {
    descriptionKey: 'models.i-i-s-flexberry-sample-logging-student.validations.studentName.__caption__',
    validators: [
      validator('ds-error'),
    ],
  },
  group: {
    descriptionKey: 'models.i-i-s-flexberry-sample-logging-student.validations.group.__caption__',
    validators: [
      validator('ds-error'),
    ],
  },
};

export let defineProjections = function (modelClass) {
  modelClass.defineProjection('StudentE', 'i-i-s-flexberry-sample-logging-student', {
    studentName: attr('Имя студента', { index: 0 }),
    age: attr('Возраст', { index: 1 }),
    sex: attr('Пол', { index: 2 }),
    group: belongsTo('i-i-s-flexberry-sample-logging-group', 'Группа', {
      groupName: attr('Название группы', { index: 4, hidden: true })
    }, { index: 3, displayMemberPath: 'groupName' })
  });

  modelClass.defineProjection('StudentL', 'i-i-s-flexberry-sample-logging-student', {
    studentName: attr('Имя студента', { index: 0 }),
    age: attr('Возраст', { index: 1 }),
    sex: attr('Пол', { index: 2 }),
    group: belongsTo('i-i-s-flexberry-sample-logging-group', 'Группа', {
      groupName: attr('Группа', { index: 3 })
    }, { index: -1, hidden: true })
  });
};
