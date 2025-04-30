import { Serializer as GroupSerializer } from
  '../mixins/regenerated/serializers/i-i-s-flexberry-sample-logging-group';
import __ApplicationSerializer from './application';

export default __ApplicationSerializer.extend(GroupSerializer, {
  /**
  * Field name where object identifier is kept.
  */
  primaryKey: '__PrimaryKey'
});
