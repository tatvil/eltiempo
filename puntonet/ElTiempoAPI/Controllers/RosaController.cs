using Microsoft.AspNetCore.Mvc;
using ElTiempoAPI.Services;

namespace ElTiempoAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class RosaController : ControllerBase
    {
        private readonly RosaService _service;

        public RosaController(RosaService service)
        {
            _service = service;
        }

        [HttpGet]
        public IActionResult Get(string ciudad, string desde)
        {
            try
            {
                var datos = _service.ObtenerDatos(ciudad, desde);
                return Ok(datos);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "ERROR API: " + ex.Message);
            }
        }

    }
}

