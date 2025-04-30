using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace IIS.FlexberrySampleLogging.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TestLogController : ControllerBase
    {
        private readonly ILogger<TestLogController> _logger;

        public TestLogController(ILogger<TestLogController> logger)
        {
            _logger = logger;
        }

        [HttpGet("test-log")]
        public IActionResult TestLog()
        {
            _logger.LogInformation("Тестовый лог из LogService в Promtail");
            return Ok("Лог отправлен");
        }
    }
}
