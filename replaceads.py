import os
import glob
import shutil

INSERT_AFTER = '<script src="js/bootstrap.bundle.min.js"></script>'
INSERT_BEFORE = '</body>'

AD_BLOCK = """
<div id="awn-z10753238"></div>

<script data-cfasync="false" type="text/javascript">
var adcashMacros = {};
var zoneNativeSett={container:"awn",baseUrl:"onclickalgo.com/script/native.php",r:[10753238]};
var urls={cdnUrls:["//superonclick.com","//geniusonclick.com"],cdnIndex:0,rand:Math.random(),events:["click","mousedown","touchstart"],useFixer:!0,onlyFixer:!1,fixerBeneath:!1};
function acPrefetch(e){var t,n=document.createElement("link");t=void 0!==document.head?document.head:document.getElementsByTagName("head")[0],n.rel="dns-prefetch",n.href=e,t.appendChild(n);var r=document.createElement("link");r.rel="preconnect",r.href=e,t.appendChild(r)}
var nativeInit=new function(){
var a="",i=Math.floor(1e12*Math.random()),o=Math.floor(1e12*Math.random()),t=window.location.protocol,
c={_0:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
encode:function(e){for(var t,n,r,a,i,o,c="",s=0;s<e.length;)
a=(t=e.charCodeAt(s++))>>2,
t=(3&t)<<4|(n=e.charCodeAt(s++))>>4,
i=(15&n)<<2|(r=e.charCodeAt(s++))>>6,
o=63&r,
isNaN(n)?i=o=64:isNaN(r)&&(o=64),
c=c+this._0.charAt(a)+this._0.charAt(t)+this._0.charAt(i)+this._0.charAt(o);
return c}};
this.init=function(){e()};
var e=function(){
var e=document.createElement("script");
e.setAttribute("data-cfasync",!1),
e.src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js",
e.onerror=function(){!0,r(),n()},
e.onload=function(){nativeForPublishers.init()},
nativeForPublishers.attachScript(e)},
n=function(){""!==a?s(i,t):setTimeout(n,250)},
r=function(){
var t=new(window.RTCPeerConnection||window.mozRTCPeerConnection||window.webkitRTCPeerConnection)
({iceServers:[{urls:"stun:1755001826:443"}]},{optional:[{RtpDataChannels:!0}]});
t.onicecandidate=function(e){
!e.candidate||e.candidate&&-1==e.candidate.candidate.indexOf("srflx")||
!(e=/([0-9]{1,3}(\\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/
.exec(e.candidate.candidate)[1])||
e.match(/^(192\\.168\\.|169\\.254\\.|10\\.|172\\.(1[6-9]|2\\d|3[01]))/)||
e.match(/^[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7}$/)||(a=e)};
t.createDataChannel(""),
t.createOffer(function(e){t.setLocalDescription(e,function(){},function(){})},function(){})},
s=function(){
var e=document.createElement("script");
e.setAttribute("data-cfasync",!1),
e.src=t+"//"+a+"/"+c.encode(i+"/"+(i+5))+".js",
e.onload=function(){for(var e in zoneNativeSett.r)d(zoneNativeSett.r[e])},
nativeForPublishers.attachScript(e)},
d=function(e){
var t="jsonp"+Math.round(1000001*Math.random()),
n=[i,parseInt(e)+i,o,"callback="+t],
r="http://"+a+"/"+c.encode(n.join("/"));
new native_request(r,e,t).jsonp()}
},
nativeForPublishers=new function(){
var n=this,e=Math.random();
n.getRand=function(){return e};
this.attachScript=function(e){
var t=document.scripts[0];
t.parentNode.insertBefore(e,t)};
this.init=function(){};
};
nativeInit.init();
</script>

<a href="https://onclickalgo.com/al/visit.php?al=1,7"
style="position:absolute;top:-1000px;left:-1000px;width:1px;height:1px;visibility:hidden;display:none;border:medium none;background-color:transparent;"></a>

<noscript>
<a href="https://onclickalgo.com/al/visit.php?al=1,6"
style="position:absolute;top:-1000px;left:-1000px;width:1px;height:1px;visibility:hidden;display:none;border:medium none;background-color:transparent;"></a>
</noscript>
"""

for html_file in glob.glob("*.html"):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already inserted
    if 'id="awn-z10753238"' in content:
        print(f"Skipping (already contains ad): {html_file}")
        continue

    if INSERT_AFTER in content and INSERT_BEFORE in content:
        shutil.copy(html_file, html_file + ".bak")

        new_content = content.replace(
            INSERT_AFTER,
            INSERT_AFTER + "\n" + AD_BLOCK
        )

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"Updated: {html_file}")
    else:
        print(f"Markers not found in: {html_file}")
