import { moduleForModel, test } from 'ember-qunit';

moduleForModel('i-i-s-flexberry-sample-logging-group', 'Unit | Model | i-i-s-flexberry-sample-logging-group', {
  // Specify the other units that are required for this test.
  needs: [
    'model:i-i-s-flexberry-sample-logging-activity',
    'model:i-i-s-flexberry-sample-logging-group',
    'model:i-i-s-flexberry-sample-logging-student',
    'validator:ds-error',
    'validator:presence',
    'validator:number',
    'validator:date',
    'validator:belongs-to',
    'validator:has-many',
    'service:syncer',
  ],
});

test('it exists', function(assert) {
  let model = this.subject();

  // let store = this.store();
  assert.ok(!!model);
});
