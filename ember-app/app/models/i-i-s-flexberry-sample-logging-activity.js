import { buildValidations } from 'ember-cp-validations';
import EmberFlexberryDataModel from 'ember-flexberry-data/models/model';

import {
  defineProjections,
  ValidationRules,
  Model as ActivityMixin
} from '../mixins/regenerated/models/i-i-s-flexberry-sample-logging-activity';

const Validations = buildValidations(ValidationRules, {
  dependentKeys: ['model.i18n.locale'],
});

let Model = EmberFlexberryDataModel.extend(ActivityMixin, Validations, {
});

defineProjections(Model);

export default Model;
