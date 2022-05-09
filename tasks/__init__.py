from invoke import Collection, task
import lambda_tasks_plugin as lambda_tasks
from lambda_tasks_plugin.test_tasks import unit_test


@task(pre=[unit_test])
def test(ctx):
    pass


namespace = Collection(lambda_tasks,
                       test)

namespace.default = 'test'
