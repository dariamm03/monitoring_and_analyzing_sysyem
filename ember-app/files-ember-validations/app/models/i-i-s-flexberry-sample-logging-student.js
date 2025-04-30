import {
  defineNamespace,
  defineProjections,
  Model as StudentMixin
} from '../mixins/regenerated/models/i-i-s-flexberry-sample-logging-student';

import EmberFlexberryDataModel from 'ember-flexberry-data/models/model';

let Model = EmberFlexberryDataModel.extend(StudentMixin, {
});

defineNamespace(Model);
defineProjections(Model);

export default Model;
