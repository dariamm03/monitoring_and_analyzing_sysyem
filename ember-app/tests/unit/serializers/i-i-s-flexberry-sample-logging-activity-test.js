import { moduleForModel, test } from 'ember-qunit';

moduleForModel('i-i-s-flexberry-sample-logging-activity', 'Unit | Serializer | i-i-s-flexberry-sample-logging-activity', {
  // Specify the other units that are required for this test.
  needs: [
    'serializer:i-i-s-flexberry-sample-logging-activity',
    'service:syncer',
    'transform:file',
    'transform:decimal',
    'transform:guid',

    'model:i-i-s-flexberry-sample-logging-activity',
    'model:i-i-s-flexberry-sample-logging-group',
    'model:i-i-s-flexberry-sample-logging-student',
    'validator:ds-error',
    'validator:presence',
    'validator:number',
    'validator:date',
    'validator:belongs-to',
    'validator:has-many',
  ],
});

// Replace this with your real tests.
test('it serializes records', function(assert) {
  let record = this.subject();

  let serializedRecord = record.serialize();

  assert.ok(serializedRecord);
});
