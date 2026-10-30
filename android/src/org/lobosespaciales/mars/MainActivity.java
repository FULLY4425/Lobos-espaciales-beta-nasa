package org.lobosespaciales.mars;

import android.app.*;
import android.os.*;
import android.content.*;
import android.net.Uri;
import android.graphics.Color;
import android.webkit.*;
import android.widget.*;
import android.view.*;
import java.net.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;

/** Local assets remain offline. Only mission API requests reach the selected Python server. */
public class MainActivity extends Activity {
    private WebView web;
    private String pendingExport;
    private ServerSocket local;
    private ExecutorService pool = Executors.newFixedThreadPool(4);
    private volatile String backend;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        backend=getPreferences(0).getString("backend", "");
        LinearLayout layout=new LinearLayout(this);layout.setOrientation(LinearLayout.VERTICAL);layout.setBackgroundColor(Color.rgb(16,20,20));
        layout.setOnApplyWindowInsetsListener((v,insets)->{v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());return insets;});
        Button settings=new Button(this);settings.setText("LOBOS MARTE · Configurar servidor Python");settings.setOnClickListener(v->configure());layout.addView(settings);
        web=new WebView(this);layout.addView(web,new LinearLayout.LayoutParams(-1,0,1));setContentView(layout);
        web.getSettings().setJavaScriptEnabled(true);web.getSettings().setDomStorageEnabled(true);web.getSettings().setAllowFileAccess(false);web.getSettings().setAllowContentAccess(false);
        web.addJavascriptInterface(new Object(){@JavascriptInterface public void saveMission(String json){if(json.length()>2000000)return;runOnUiThread(()->{pendingExport=json;Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT);intent.setType("application/json");intent.addCategory(Intent.CATEGORY_OPENABLE);intent.putExtra(Intent.EXTRA_TITLE,"lobos-espaciales-mision.json");startActivityForResult(intent,42);});}},"AndroidMission");
        web.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request){Uri u=request.getUrl();if(u.getHost()!=null&&u.getHost().equals("127.0.0.1")&&u.getPort()==local.getLocalPort())return false;if("https".equals(u.getScheme())||"http".equals(u.getScheme())){startActivity(new Intent(Intent.ACTION_VIEW,u));}return true;}});
        try {
            local=new ServerSocket(0,16,InetAddress.getByName("127.0.0.1"));
            Thread accept=new Thread(()->{while(!local.isClosed()){try{Socket client=local.accept();pool.execute(()->serve(client));}catch(IOException ignored){break;}}});accept.setDaemon(true);accept.start();
            web.loadUrl("http://127.0.0.1:"+local.getLocalPort()+"/");
        } catch(IOException e){new AlertDialog.Builder(this).setMessage("No se pudo iniciar el mapa local.").setPositiveButton("Cerrar",(d,w)->finish()).show();}
        if(backend.isEmpty())new AlertDialog.Builder(this).setTitle("Bienvenido a Marte").setMessage("El mapa y los datos están incluidos. Para calcular y exportar rutas, configura la dirección de tu servidor Python. Puedes hacerlo después desde el botón superior.").setPositiveButton("Ver mapa",null).setNeutralButton("Configurar",(d,w)->configure()).show();
    }
    private void configure(){
        EditText input=new EditText(this);input.setSingleLine(true);input.setHint("http://192.168.1.25:5173");input.setText(backend);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Servidor Python").setMessage("Usa HTTPS para un servidor público o HTTP solo en tu Wi-Fi privada. La computadora debe estar encendida. No uses localhost: apunta al teléfono. Deja vacío para usar solo el mapa.").setView(input).setPositiveButton("Guardar",null).setNegativeButton("Cancelar",null).create();
        dialog.setOnShowListener(v->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(b->{String value=input.getText().toString().trim().replaceAll("/+$","");try{if(!value.isEmpty()){URI u=new URI(value);if(!("https".equals(u.getScheme())||"http".equals(u.getScheme()))||u.getHost()==null||u.getUserInfo()!=null||u.getQuery()!=null||u.getFragment()!=null||!(u.getPath().isEmpty()||u.getPath().equals("/")))throw new Exception();}backend=value;getPreferences(0).edit().putString("backend",value).apply();dialog.dismiss();Toast.makeText(this,"Configuración guardada",Toast.LENGTH_SHORT).show();}catch(Exception e){input.setError("Introduce una dirección HTTP/HTTPS sin ruta ni credenciales.");}}));dialog.show();
    }
    private String line(InputStream in)throws IOException{ByteArrayOutputStream out=new ByteArrayOutputStream();for(int c;(c=in.read())!=-1;){if(c==10)break;if(c!=13)out.write(c);if(out.size()>8192)throw new IOException();}return out.toString("UTF-8");}
    private void serve(Socket socket){try(Socket client=socket){client.setSoTimeout(15000);InputStream in=client.getInputStream();String[] request=line(in).split(" ");if(request.length<2)return;String method=request[0],path=request[1].split("\\?")[0];int length=0;for(String h;!(h=line(in)).isEmpty();){if(h.toLowerCase().startsWith("content-length:"))length=Integer.parseInt(h.substring(15).trim());}if(length<0||length>16384){reply(client,413,"application/json","{}".getBytes());return;}
        if(path.equals("/api/plan")||path.equals("/api/export")){
            if(!method.equals("POST")){reply(client,405,"application/json","{}".getBytes());return;}
            byte[] body=new byte[length];int count=0;while(count<length){int n=in.read(body,count,length-count);if(n<0)throw new IOException();count+=n;}
            if(backend.isEmpty()){reply(client,503,"application/json","{\"error\":\"Configura el servidor Python desde el botón superior para calcular rutas.\"}".getBytes(StandardCharsets.UTF_8));return;}
            HttpURLConnection connection=null;
            try{connection=(HttpURLConnection)new URL(backend+path).openConnection();connection.setInstanceFollowRedirects(false);connection.setConnectTimeout(10000);connection.setReadTimeout(30000);connection.setRequestMethod("POST");connection.setDoOutput(true);connection.setRequestProperty("Content-Type","application/json");connection.getOutputStream().write(body);int code=connection.getResponseCode();InputStream response=code>=400?connection.getErrorStream():connection.getInputStream();byte[] bytes=response==null?"{}".getBytes():readAll(response);reply(client,code,"application/json; charset=utf-8",bytes);}catch(IOException e){reply(client,503,"application/json","{\"error\":\"No se pudo conectar al servidor Python. Comprueba su dirección y la red Wi-Fi.\"}".getBytes(StandardCharsets.UTF_8));}finally{if(connection!=null)connection.disconnect();}return;
        }
        if(!method.equals("GET")||path.contains("..")||!(path.equals("/")||path.equals("/index.html")||path.startsWith("/src/")||path.startsWith("/public/")||path.startsWith("/docs/"))){reply(client,404,"text/plain",new byte[0]);return;}
        String file=path.equals("/")?"index.html":path.substring(1);try(InputStream asset=getAssets().open(file)){String type=file.endsWith(".js")?"text/javascript":file.endsWith(".css")?"text/css":file.endsWith(".json")?"application/json":file.endsWith(".html")?"text/html":file.endsWith(".png")?"image/png":"text/plain";reply(client,200,type,readAll(asset));}catch(IOException e){reply(client,404,"text/plain",new byte[0]);}
    }catch(Exception ignored){}}
    private byte[] readAll(InputStream in)throws IOException{ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;while((n=in.read(buffer))!=-1){out.write(buffer,0,n);if(out.size()>8*1024*1024)throw new IOException();}return out.toByteArray();}
    private void reply(Socket s,int status,String type,byte[] body)throws IOException{OutputStream out=s.getOutputStream();out.write(("HTTP/1.1 "+status+" Response\r\nContent-Type: "+type+"\r\nContent-Length: "+body.length+"\r\nConnection: close\r\n\r\n").getBytes(StandardCharsets.US_ASCII));out.write(body);out.flush();}
    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==42&&result==RESULT_OK&&data!=null&&data.getData()!=null&&pendingExport!=null){try(OutputStream out=getContentResolver().openOutputStream(data.getData())){out.write(pendingExport.getBytes(StandardCharsets.UTF_8));Toast.makeText(this,"Misión guardada",Toast.LENGTH_SHORT).show();}catch(IOException e){Toast.makeText(this,"No se pudo guardar la misión",Toast.LENGTH_LONG).show();}}pendingExport=null;}
    @Override public void onBackPressed(){if(web.canGoBack())web.goBack();else super.onBackPressed();}
    @Override protected void onDestroy(){try{if(local!=null)local.close();}catch(IOException ignored){}pool.shutdownNow();if(web!=null)web.destroy();super.onDestroy();}
}
