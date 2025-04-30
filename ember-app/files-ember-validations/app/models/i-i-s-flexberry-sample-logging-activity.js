import {
  defineNamespace,
  defineProjections,
  Model as ActivityMixin
} from '../mixins/regenerated/models/i-i-s-flexberry-sample-logging-activity';

import EmberFlexberryDataModel from 'ember-flexberry-data/models/model';

let Model = EmberFlexberryDataModel.extend(ActivityMixin, {
});

defineNamespace(Model);
defineProjections(Model);

export default Model;
