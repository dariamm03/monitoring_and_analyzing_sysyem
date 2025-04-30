import { buildValidations } from 'ember-cp-validations';
import EmberFlexberryDataModel from 'ember-flexberry-data/models/model';

import {
  defineProjections,
  ValidationRules,
  Model as StudentMixin
} from '../mixins/regenerated/models/i-i-s-flexberry-sample-logging-student';

const Validations = buildValidations(ValidationRules, {
  dependentKeys: ['model.i18n.locale'],
});

let Model = EmberFlexberryDataModel.extend(StudentMixin, Validations, {
});

defineProjections(Model);

export default Model;
