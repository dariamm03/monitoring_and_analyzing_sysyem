import { Serializer as ActivitySerializer } from
  '../mixins/regenerated/serializers/i-i-s-flexberry-sample-logging-activity';
import __ApplicationSerializer from './application';

export default __ApplicationSerializer.extend(ActivitySerializer, {
  /**
  * Field name where object identifier is kept.
  */
  primaryKey: '__PrimaryKey'
});
