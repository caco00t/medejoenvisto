// Servidor mínimo de Me Dejó en Visto: sirve la página y valida códigos de regalo de un solo uso.
const REGALOS = new Set(["a6b699e9a4007a15e22be54394b80fc241db8c5fef2e26d1dcb6a09fea7fa066", "cace5c6f3bd20a52fd4a4087a54fef89b920c2c9c3f25945a6b8891ba8ec92ae", "dd6fb11c3bb23b725275a85893bc04c61cdb18581d25bbfe45d40e90730e42b7", "3508a20822079d733a208b3011ed2a44d416f8f44dddb88d233c4e6227611e35", "d754ae523bc7e21feb6d6c52467fe54dd37e6ec23ecb421adef430ad9e38c54f", "fac7f2b996fe6d739a27899d68b35133d1bf7fee5523a9d9bdd4c010e849f231", "1213a288a953538800d558279f6471052a5e50f45ae92662a6eba7c84dea8d14", "f188017fac51e4c51fe4aba76bfc5546962a95bb5e340ba01e6fba2a08c54441", "30f781981b912ef5c7bd005ee824f92bfeaa8fee7dc284fe61a65f60b088f71a", "f7f4b0b475dfdd74bd704fd421f5a8bfc9dad75a439acd9c679631b7157dd2d6", "aff5c251aaf0c1c7856de6a02a68386721f375a2c561e7e4748a9ba1af3ebb6e", "5a403d5cbde19b1cee5cafd958f86a0757ba0e32e9837946fc6610e35b009029", "7695fca2f505abe4bba230f222ee2044fe0b49d14bf540c47b02bf6b8dbbb96f", "ab980cbc7b592aecc1fe94011d9fa73517c39e83f1d6a01e31f20a994ab6dc1c", "f527343ae578afba30e8ebd61ab41f772134d33d36bfd09da431a325fada6f8b", "b210d77444c860aa612a85e564efa9fd27efcf55f7ab492fd2717854c86b74d0", "aed09a793f3653c09a3f28affd207c0140c8933adbbe41e558936a9547288b85", "c188a51bc9813bf488e82af943e0adb4f8f81e26d670fb46e093adce37aa0736", "b559983f218e2ab5cb668991915472268adc7c582d91aea4c426d62a001a7f92", "d30007b915bffa6a0c6ada5641659f23700db89af7239fa9b5c490d6911b25f7", "c556278927e3bbcffb542c4070c9b5a5fb86f00b46dd6208b529948fc3628c5a", "b04b9aaf0093b2b513db217de769bc6f06cb7d7e24e047db00704a04f25a2f6e", "801460f3e30e2848cd125c06db816ba5375c69bb7f3c723af77f844311106183", "af11b60dc79cd330ff40f10c86cca95966b92cd4ff738ac9c5dca5162fe69dc2", "dc4a2dacef8f0121202777ea2472cb55e4d4ad090d6b319c3604f94557d34974", "c330e40adabe09ffab1bb222010bf02d2dfdb8d557b687f7fdbf2156ee4c7d4e", "dd6db69b37d2fc12e87630dd3636cc5aa3d8df10eec3756eec30d9b4d4bb821f", "405a575b1da2014c47a1377783486089042be33f3d212f2ecdfe7ed0e8bde593", "5ac880827f5cb474a87e2d8dacd51681040e417c9aadd8d5e4d3ddce6fbebfc2", "ff660b64b1322158ab2e4d31bdb2c8cd383e38fe37784372636ca2e0aa96bdc3"]);
const DIAS = 7;
const EVENTOS = new Set(['visita','archivo','resumen','pago_click','pago_ok','informe']);
async function sha(t){ const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)); return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join(''); }
const json = (o, st=200) => new Response(JSON.stringify(o), {status: st, headers: {'content-type':'application/json', 'cache-control':'no-store'}});
export default {
  async fetch(req, env){
    const url = new URL(req.url);
    if (url.pathname === '/api/regalo' && req.method === 'POST'){
      let body; try{ body = await req.json(); }catch(e){ return json({estado:'error'}, 400); }
      const code = String(body.code||'').trim().toUpperCase().slice(0,40);
      const device = String(body.device||'').slice(0,64);
      if (!code || device.length < 16) return json({estado:'error'}, 400);
      const h = await sha(code);
      if (!REGALOS.has(h)) return json({estado:'invalido'});
      const key = 'usado:' + h;
      const prev = await env.REGALOS_KV.get(key, 'json');
      const now = Date.now();
      if (!prev){ await env.REGALOS_KV.put(key, JSON.stringify({device, t: now})); return json({estado:'ok', desde: now}); }
      if (prev.device !== device) return json({estado:'usado'});
      if (now - prev.t > DIAS*86400000) return json({estado:'vencido'});
      return json({estado:'ok', desde: prev.t});
    }
    if (url.pathname === '/api/e' && req.method === 'POST'){
      // Embudo anónimo: solo suma conteos diarios por paso. No recibe datos del chat ni de la persona.
      const n = url.searchParams.get('n'), ed = url.searchParams.get('ed') === 'completa' ? 'completa' : 'gratis';
      if (!EVENTOS.has(n)) return new Response(null, {status: 204});
      const d = new Date(Date.now() - 5*3600000).toISOString().slice(0,10);
      const key = 'ev:' + d + ':' + ed + ':' + n;
      const v = parseInt(await env.REGALOS_KV.get(key) || '0', 10);
      await env.REGALOS_KV.put(key, String(v + 1), {expirationTtl: 400*86400});
      return new Response(null, {status: 204});
    }
    if (url.pathname === '/api/stats'){
      const out = {}; let cursor;
      do { const l = await env.REGALOS_KV.list({prefix: 'ev:', cursor}); for (const k of l.keys){ const [, d, ed, n] = k.name.split(':'); ((out[d] ||= {})[ed] ||= {})[n] = parseInt(await env.REGALOS_KV.get(k.name) || '0', 10); } cursor = l.list_complete ? null : l.cursor; } while (cursor);
      return json(out);
    }
    return env.ASSETS.fetch(req);
  }
};
