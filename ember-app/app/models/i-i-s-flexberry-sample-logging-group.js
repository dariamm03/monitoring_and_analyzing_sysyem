import { buildValidations } from 'ember-cp-validations';
import EmberFlexberryDataModel from 'ember-flexberry-data/models/model';

import {
  defineProjections,
  ValidationRules,
  Model as GroupMixin
} from '../mixins/regenerated/models/i-i-s-flexberry-sample-logging-group';

const Validations = buildValidations(ValidationRules, {
  dependentKeys: ['model.i18n.locale'],
});

let Model = EmberFlexberryDataModel.extend(GroupMixin, Validations, {
});

defineProjections(Model);

export default Model;
