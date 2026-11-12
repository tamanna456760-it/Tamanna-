(()=>{"use strict";
const $=id=>document.getElementById(id);
const banner=$("modeBanner"),status=$("systemStatus"),logout=$("adminLogout");
function setPreview(reason){
  banner.textContent="PREVIEW MODE — Admin interface is running without a backend API. Live data and management actions are disabled. "+reason;
  banner.classList.add("preview");
  status.textContent="API not connected";
  status.classList.remove("online");
  $("adminIdentity").textContent="Offline preview";
  $("adminName").textContent="Tamanna AI Admin";
  $("adminEmail").textContent="Backend connection required";
  logout.hidden=true;
}
function setLive(data){
  const admin=data.admin||{},system=data.system||{};
  $("adminIdentity").textContent=admin.email||"Administrator";
  $("adminName").textContent=admin.name||"Administrator";
  $("adminEmail").textContent=admin.email||"";
  $("backendStatus").textContent=system.status||"Online";
  $("modelProvider").textContent=system.model_provider||"Not configured";
  $("environment").textContent=system.environment||"Unknown";
  $("database").textContent=system.database||"Not configured";
  banner.textContent="LIVE MODE — Administrator permission was verified by the backend.";
  banner.classList.remove("preview","error");
  status.textContent="● Backend connected";
  status.classList.add("online");
  logout.hidden=false;
}
async function connect(){
  try{
    const response=await fetch("/api/admin/overview",{credentials:"same-origin",headers:{Accept:"application/json"}});
    const data=await response.json().catch(()=>({}));
    if(response.status===401||response.status===403){
      banner.textContent=response.status===401?"Admin sign-in required. Open User Chat, sign in with the allowlisted account, then revisit /admin.":"Access denied. This signed-in account is not authorized as an administrator.";
      banner.classList.add("error");status.textContent="Access denied";$("adminContent").hidden=true;return;
    }
    if(!response.ok)throw new Error(data.detail||("HTTP "+response.status));
    if(data.ok!==true||!data.admin)throw new Error("Unexpected API response");
    setLive(data);
  }catch(error){
    setPreview("The API endpoint is not available yet ("+(error.message||"network error")+").");
  }
}
logout.addEventListener("click",async()=>{
  logout.disabled=true;
  try{await fetch("/api/auth/logout",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:"{}"});}
  finally{location.href="/";}
});
const auditButton=$("runEthicalAudit"),auditStatus=$("ethicalAuditStatus"),auditReport=$("ethicalAuditReport");
if(auditButton&&auditStatus&&auditReport){
  auditButton.addEventListener("click",async()=>{
    auditButton.disabled=true;
    auditStatus.textContent="Running read-only checks…";
    auditReport.textContent="Tamanna AI security configuration পরীক্ষা করা হচ্ছে…";
    try{
      const response=await fetch("/api/admin/security/ethical-audit",{
        method:"GET",credentials:"same-origin",headers:{Accept:"application/json"}
      });
      const data=await response.json().catch(()=>({}));
      if(response.status===401||response.status===403){
        auditStatus.textContent="Admin access required";
        auditReport.textContent=data.detail||"Administrator permission was not verified.";
        return;
      }
      if(!response.ok||data.ok!==true||!data.audit)throw new Error(data.detail||("HTTP "+response.status));
      const report=data.audit;
      auditStatus.textContent=report.summary.status+" · "+report.summary.passed+"/"+report.summary.total+" passed";
      auditReport.textContent=[
        "TAMANNA AI — ETHICAL SECURITY AUDIT",
        "Mode: "+report.mode,
        "Summary: "+JSON.stringify(report.summary),
        "",
        ...report.checks.map(item=>item.status+" | "+item.name+" | "+item.detail),
        "",
        "LIMITATIONS",
        ...report.limitations.map(item=>"- "+item)
      ].join("\n");
    }catch(error){
      auditStatus.textContent="Audit unavailable";
      auditReport.textContent="নিরাপত্তা audit চালানো যায়নি: "+(error.message||"network error");
    }finally{
      auditButton.disabled=false;
    }
  });
}

const antivirusForm=$("antivirusForm"),antivirusFile=$("antivirusFile"),antivirusButton=$("antivirusScanButton"),antivirusStatus=$("antivirusScanStatus"),antivirusReport=$("antivirusScanReport");
if(antivirusForm&&antivirusFile&&antivirusButton&&antivirusStatus&&antivirusReport){
  antivirusForm.addEventListener("submit",async event=>{
    event.preventDefault();
    const file=antivirusFile.files&&antivirusFile.files[0];
    if(!file){antivirusStatus.textContent="Choose a file first";return;}
    if(file.size>10*1024*1024){antivirusStatus.textContent="File exceeds 10 MiB limit";antivirusReport.textContent="এই endpoint সর্বোচ্চ 10 MiB ফাইল scan করে।";return;}
    antivirusButton.disabled=true;
    antivirusStatus.textContent="Uploading to temporary scanner…";
    antivirusReport.textContent="ফাইলটি ClamAV দিয়ে পরীক্ষা করা হচ্ছে।";
    try{
      const form=new FormData();
      form.append("file",file,file.name);
      const response=await fetch("/tamanna-ai/security/antivirus/scan-upload",{
        method:"POST",credentials:"same-origin",headers:{Accept:"application/json"},body:form
      });
      const data=await response.json().catch(()=>({}));
      if(response.status===401||response.status===403){
        antivirusStatus.textContent="Admin access required";
        antivirusReport.textContent=data.detail||"Administrator permission was not verified.";
        return;
      }
      if(response.status===503){
        const detail=data.detail||{};
        antivirusStatus.textContent="Scan not verified";
        antivirusReport.textContent=typeof detail==="string"?detail:JSON.stringify(detail,null,2);
        return;
      }
      if(response.status===413){
        antivirusStatus.textContent="File too large";
        antivirusReport.textContent=data.detail||"Maximum upload size is 10 MiB.";
        return;
      }
      if(!response.ok||!data.scan)throw new Error(data.detail||("HTTP "+response.status));
      const scan=data.scan;
      antivirusStatus.textContent=scan.status==="clean"?"Clean · ClamAV scan completed":scan.status==="infected"?"Malware detected":"Scan status: "+scan.status;
      antivirusReport.textContent=[
        "TAMANNA AI ANTIVIRUS",
        "File: "+(data.filename||file.name),
        "Status: "+scan.status,
        "Message: "+scan.message,
        "Stored: "+String(data.stored===true),
        "Executed: "+String(data.executed===true),
        "",
        "A clean result is not a guarantee that a file is safe."
      ].join("\n");
    }catch(error){
      antivirusStatus.textContent="Scanner unavailable";
      antivirusReport.textContent="Antivirus scan চালানো যায়নি: "+(error.message||"network error");
    }finally{
      antivirusButton.disabled=false;
    }
  });
}

connect();
})();