import { Serializer as StudentSerializer } from
  '../mixins/regenerated/serializers/i-i-s-flexberry-sample-logging-student';
import __ApplicationSerializer from './application';

export default __ApplicationSerializer.extend(StudentSerializer, {
  /**
  * Field name where object identifier is kept.
  */
  primaryKey: '__PrimaryKey'
});
