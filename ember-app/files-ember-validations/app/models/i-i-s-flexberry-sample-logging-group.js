import {
  defineNamespace,
  defineProjections,
  Model as GroupMixin
} from '../mixins/regenerated/models/i-i-s-flexberry-sample-logging-group';

import EmberFlexberryDataModel from 'ember-flexberry-data/models/model';

let Model = EmberFlexberryDataModel.extend(GroupMixin, {
});

defineNamespace(Model);
defineProjections(Model);

export default Model;
