# Catálogo de Correos de Prueba (Testing Pool) - Detector de Spam

Este archivo contiene un catálogo de **24 correos de prueba seleccionados** para evaluar el clasificador de Spam en español e inglés.

Cada ejemplo incluye:
* **ID:** Número identificador.
* **Tipo Esperado:** `SPAM` o `HAM` (legítimo).
* **Idioma:** `ES` (Español) o `EN` (Inglés).
* **Categoría:** Tipo de correo o ataque.
* **Texto para probar:** Texto listo para copiar o evaluar por ID.

---

## 🛑 Correos de SPAM en Español (IDs 1 al 8)

### ID 1: Lotería / Premio Falso
* **Asunto:** ¡FELICIDADES! Reclama tu premio de 1,000,000 USD hoy
* **Esperado:** `SPAM`
* **Texto:**
```text
¡Felicidades! Su dirección de correo electrónico ha sido seleccionada como ganadora de 1,000,000 USD en nuestra lotería internacional anual. Para reclamar su premio en efectivo libre de impuestos, haga clic aquí de inmediato: http://reclamar-premio-seguro.com. Oferta urgente válida solo por 24 horas.
```

### ID 2: Phishing Bancario
* **Asunto:** ALERTA URGENTE: Su cuenta bancaria ha sido suspendida
* **Esperado:** `SPAM`
* **Texto:**
```text
Estimado cliente, hemos detectado accesos no autorizados a su banca en línea. Por motivos de seguridad su cuenta ha sido suspendida temporalmente. Para desbloquearla y verificar su identidad, ingrese sus datos de acceso y tarjeta en http://banco-seguro-actualizacion.net inmediatamente o su cuenta será cancelada definitivamente.
```

### ID 3: Farmacia en Línea Ilegal
* **Asunto:** Oferta especial: Viagra y Cialis genérico con 70% de descuento
* **Esperado:** `SPAM`
* **Texto:**
```text
Compre viagra, cialis y levitra genérico de máxima calidad al mejor precio del mercado. Sin receta médica, pago 100% seguro con tarjeta o cripto y envío discreto hasta la puerta de su casa en 48 horas. Aproveche la promoción con 70% de descuento haciendo clic aquí: www.farmacia-online-descuento.com
```

### ID 4: Criptomonedas / Esquema Ponzi
* **Asunto:** Multiplica tus Bitcoins: Retorno del 300% garantizado en 7 días
* **Esperado:** `SPAM`
* **Texto:**
```text
Descubre la plataforma de inversión automatizada con inteligencia artificial que genera ingresos pasivos garantizados. Deposita desde $100 USD en Bitcoin o USDT y recibe un 300% de ganancia en solo 7 días sin ningún riesgo. Miles de personas ya son millonarias. Regístrate hoy en http://cripto-ganancias-automaticas.org
```

### ID 5: Préstamo Express Fraudulento
* **Asunto:** Préstamo personal preaprobado de hasta $50,000 USD sin aval
* **Esperado:** `SPAM`
* **Texto:**
```text
Crédito express aprobado en 15 minutos sin revisar buró de crédito ni solicitar avales ni garantías. Tasa fija de interés del 1% mensual. Solo responda a este correo con su nombre completo, número de teléfono y comprobante de domicilio a credito.inmediato@financiera-rapida.com para desembolsar su dinero hoy mismo.
```

### ID 6: Herencia / Notificación de Abogado Falso
* **Asunto:** Propuesta confidencial sobre herencia no reclamada
* **Esperado:** `SPAM`
* **Texto:**
```text
Soy el abogado Williams Smith, albacea de un cliente fallecido en el extranjero que dejó un fondo no reclamado de 8.5 millones de dólares en un banco internacional. Al compartir el mismo apellido, propongo presentarlo a usted como beneficiario legítimo para dividir los fondos en un 50% para cada uno. Mantenga estricta confidencialidad y responda con urgencia a mi correo privado.
```

### ID 7: Falsa Alerta de PayPal / Pasarela de Pago
* **Asunto:** Aviso de seguridad: Transacción no reconocida de $489.99 USD
* **Esperado:** `SPAM`
* **Texto:**
```text
Notificación de PayPal: Se ha registrado un cargo de $489.99 USD a nombre de Electronics Store LLC. Si usted no reconoce esta transacción, haga clic inmediatamente en cancelar transacción para revertir el cobro antes de 12 horas: http://verificacion-transaccion-paypal.com
```

### ID 8: Oferta Laboral Falsa
* **Asunto:** Vacante urgente: Trabaja desde casa y gana $300 a $800 diarios
* **Esperado:** `SPAM`
* **Texto:**
```text
Empresa global busca personal para trabajo remoto a tiempo parcial evaluando videos y procesando datos. No requiere experiencia previa, solo computadora o celular e internet. Horario flexible de 2 horas al día con pago diario por transferencia. Cupos limitados. Empieza de inmediato escribiendo por WhatsApp o en http://empleo-remoto-express.net
```

---

## ✅ Correos Legítimos (HAM) en Español (IDs 9 al 16)

### ID 9: Reunión y Seguimiento de Proyecto
* **Asunto:** Minuta de la reunión de seguimiento y acuerdos del sprint
* **Esperado:** `HAM`
* **Texto:**
```text
Hola a todos, les comparto el resumen de la reunión de hoy sobre el avance del proyecto. Acordamos que el equipo de frontend entregará los módulos de visualización este jueves y el equipo de backend integrará las APIs el viernes. Quedamos atentos a cualquier duda antes de la sesión de sincronización del próximo lunes. Saludos cordiales.
```

### ID 10: Contrato Comercial de Suministro
* **Asunto:** Revisión del contrato de suministro y propuesta de tarifas
* **Esperado:** `HAM`
* **Texto:**
```text
Estimado Carlos, adjunto encontrarás el borrador del acuerdo de suministro de gas natural y la tabla de tarifas actualizada para el próximo trimestre. Te agradeceré que el equipo legal revise las cláusulas de entrega y penalizaciones antes del comité de operaciones de mañana. Quedo a tu disposición si requieres aclaraciones técnicas.
```

### ID 11: Finanzas Corporativas y Presupuesto
* **Asunto:** Reporte financiero del tercer trimestre y proyecciones de flujo
* **Esperado:** `HAM`
* **Texto:**
```text
Buenos días, adjunto el informe con el balance general consolidado y el estado de resultados correspondiente al Q3. Destaca un incremento del 8% en el margen operativo y un control efectivo de los gastos administrativos. Por favor revisen la hoja de cálculo anexa antes de la presentación con la junta directiva este jueves.
```

### ID 12: Auditoría Interna y Cumplimiento
* **Asunto:** Cronograma de la auditoría interna de procesos operativos
* **Esperado:** `HAM`
* **Texto:**
```text
Estimados gerentes de área, a partir del próximo martes iniciaremos la auditoría anual de cumplimiento normativo y control interno. Les solicitamos tener disponibles los expedientes de compras y los registros de conciliación bancaria de los últimos seis meses. Estaremos entrevistando a los líderes de equipo según el calendario anexo.
```

### ID 13: Recursos Humanos / Coordinación de Entrevista
* **Asunto:** Confirmación de entrevista técnica para la posición de analista
* **Esperado:** `HAM`
* **Texto:**
```text
Estimada Mariana, muchas gracias por tu interés en formar parte de nuestro equipo. Nos gustaría coordinar la entrevista técnica para la posición de analista de datos. Te proponemos reunirnos el próximo miércoles a las 10:00 AM mediante la plataforma Teams. Por favor confírmanos si este horario te resulta conveniente. Saludos cordiales.
```

### ID 14: Soporte Técnico / Mantenimiento de Servidores
* **Asunto:** Aviso de ventana de mantenimiento programado en servidores
* **Esperado:** `HAM`
* **Texto:**
```text
Equipo, les informamos que este sábado entre las 22:00 y las 02:00 horas se realizará una actualización de seguridad en los servidores de bases de datos. Durante este periodo los servicios internos de consulta podrían presentar intermitencias breves. Si experimentan alguna incidencia posterior, favor de reportarla a la mesa de ayuda.
```

### ID 15: Compras y Facturación Electrónica
* **Asunto:** Orden de compra recibida y factura electrónica emitida
* **Esperado:** `HAM`
* **Texto:**
```text
Apreciable proveedor, acusamos recibo de la orden de compra OC-2026-849 por el suministro de material de oficina. Le confirmamos que los insumos fueron recibidos a entera satisfacción en el almacén central. Adjuntamos la factura electrónica correspondiente para su trámite de pago en el calendario establecido.
```

### ID 16: Consultoría y Agradecimiento de Cliente
* **Asunto:** Agradecimiento por la entrega del informe de consultoría
* **Esperado:** `HAM`
* **Texto:**
```text
Estimado Roberto, queríamos agradecerte a ti y a tu equipo por la dedicación en la entrega final del diagnóstico de optimización energética. Los hallazgos presentados en el informe han sido sumamente valiosos para definir el plan estratégico de la planta. Esperamos colaborar nuevamente en futuros proyectos.
```

---

## 🌐 Correos de SPAM en Inglés (IDs 17 al 20)

### ID 17: Fraude Nigeriano Clásico
* **Asunto:** Urgent and confidential proposal from barrister Johnson
* **Esperado:** `SPAM`
* **Texto:**
```text
Dear friend, I am Barrister David Johnson, legal counsel to a late foreign investor who left an unallocated fund of $12.5M USD in an escrow account. I am contacting you to act as the next of kin to receive the transfer into your account. A 40% share will be allocated to you. Contact me immediately with your full banking coordinates.
```

### ID 18: Farmacia en Inglés
* **Asunto:** Super generic viagra and cialis at lowest online prices
* **Esperado:** `SPAM`
* **Texto:**
```text
Save up to 80% on brand new generic medications. Genuine viagra, cialis, and sleep aids with discreet worldwide shipping and no doctor prescription required. Fast delivery directly to your door. Visit our online pharmacy catalog at http://cheap-meds-discount.net now to place your order.
```

### ID 19: BEC Scam (Suplantación de CEO)
* **Asunto:** Urgent wire payment request - CEO instructions
* **Esperado:** `SPAM`
* **Texto:**
```text
Are you at your desk right now? I need an urgent wire transfer processed for an ongoing acquisition before the close of business today. The vendor account details are attached. Please process $48,500 immediately and confirm when the funds have been dispatched. Do not call, I am currently in a closed meeting.
```

### ID 20: Cripto Especulativo (Pump and Dump)
* **Asunto:** Next 100x crypto gem alert: Buy before the public announcement
* **Esperado:** `SPAM`
* **Texto:**
```text
Breaking news for investors: A major partnership will be unveiled tomorrow for token SYMB. The price is currently under $0.05 and is expected to surge by over 1,500% within hours. Accumulate your position immediately on decentralized exchanges before liquidity is unlocked: http://crypto-insider-gem.org
```

---

## 🏢 Correos Legítimos (HAM) en Inglés - Estilo Enron (IDs 21 al 24)

### ID 21: Gestión de Riesgo (Risk Management)
* **Asunto:** Agenda for tomorrow's risk management committee meeting
* **Esperado:** `HAM`
* **Texto:**
```text
Hi Vince, please find attached the revised presentation regarding power price volatility in the Western power grid for tomorrow's risk management meeting. We have updated the forward curves and value-at-risk estimates based on yesterday's settlement prices. Let me know if you would like to discuss any adjustments beforehand. Regards, Phillip.
```

### ID 22: Operaciones y Nominaciones de Gas Natural
* **Asunto:** HPL daily actuals and pipeline volume allocations for next week
* **Esperado:** `HAM`
* **Texto:**
```text
Team, attached are the Houston Pipe Line actual volume allocations and nominations for the upcoming cycle. Please review the physical flow balances for the south Texas interconnect points and notify the gas trading desk if any operational imbalances need to be reconciled prior to the evening nomination deadline.
```

### ID 23: Regulación FERC y Conferencia
* **Asunto:** Summary notes on FERC regulatory action and conference call briefing
* **Esperado:** `HAM`
* **Texto:**
```text
Colleagues, attached is a brief memorandum summarizing the recent FERC order imposing price mitigation in the western wholesale electricity market. Dynegy and Enron representatives will host a joint briefing call this afternoon at 2:00 PM EST to address questions on compliance and customer contract implications.
```

### ID 24: Itinerario de Viaje Corporativo
* **Asunto:** Travel itinerary and hotel confirmation for Tokyo visit
* **Esperado:** `HAM`
* **Texto:**
```text
Sally, here is the confirmed travel schedule for Eugenio's assignment in Tokyo next month. The flight reservations, corporate apartment booking, and local contact numbers are detailed in the attached document. Please review and let human resources know if any additional visa clearance is required.
```
