/*
 * Read-only I55 NPZ raw-source witness, designed for the connected GitHub tool.
 * The array decoding and hashes are pure JavaScript: no Node, no optimizer.
 * Do NOT claim full 620/620 replay from a proper subset.
 * This is a checked helper for archival reproducibility, NOT new research runs.
 */
"use strict";
const I55_ORIGINAL_COMMIT = "6b56fbc53ffc4d275ecef5e911ea4663474c9a08";
const I55_REPO = "owlCoder/gadapt";
const I55_BASE = "research/results/iteration55/traces/";
const I55_MANIFEST = "research/i65/archive_review/I65_I55_ORIGINAL_620_NPZ_GIT_BLOB_MANIFEST_2026-11-03.json";
const I55_PINNED_MANIFEST_BLOB = "50ca2e96762447070a74309850cb1aa6586d3eb3";
const I55_PINNED_CELLS = {
    baybe:"244296e9297e3aa1640673ee028aa1f2f784f0ff", bayes_opt:"64ceed52bbc228296691721b4fc4672999c4e341",
    bofire:"55a1f8e145f10466fae08f41d555447877769fcd", cma:"99f0ebc95004f8f771a43accb8ebb4bbd887a862",
    cmaes:"b0af13eb45fca4fdde2e47744452f40f1c63d8cb", deap:"532f070501578d29d452be5f1a18cd1cf6883318",
    emukit:"c712f0f10c33137f522967ffbc7136a6a16db40b", evolopy:"63b1df3e2373869a44eebf365fc0a982e84cf4d1",
    evotorch:"651bf5d1d782bc5afb26b6a648d2219ba1d89537", evox:"debf2e9a880a70c4ac906ba2c15b728212b84074",
    geneticalgorithm:"2a2b1360f6bb0be7644fca74decf0073160fbc40",gfo:"3837984908a81e51213e5cc350273614eab461ac",
    nevergrad:"f97f7e6ce48fc69ef1ff8c5177f5a7eec7fe3f76", niapy:"c7bdcaa3c89dd8ec178f5d2620c5354a45fe4894",
    optuna:"779c7cfd7dd79a48aa6edb8f637c194a1f5131aa",pygad:"7b34d70482e952e4c229338a837f0171b5e83282",
    pymoo:"2a5ac44e4c62f86ebb43dba6ccc3a2bd9db7e79e",pyswarms:"72fffb230fd464834403a6de138e157aee0e6e27",
    scikit_opt:"e5cf9ef291eed46b565a75ce80c9f3f6cee2aa19",scipy_de:"68198ace7b3dc7185e31d92bea27dc7905ddae50",
    smac:"aee6add993eaf400f4026a8a0448b66c87173b75"
};
function i55Assert(ok,message){if(!ok)throw Error(message)}
function i55Decode64(str){
 str=str.replace(/\s/g,""); const abc="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",map=new Int16Array(128).fill(-1);
 for(let i=0;i<64;i++)map[abc.charCodeAt(i)]=i;
 i55Assert(str.length%4===0 && /^[A-Za-z0-9+/]*={0,2}$/.test(str),"Base64 format invalid");
 const out=new Uint8Array(str.length*3/4-(str.endsWith("==")?2:str.endsWith("=")?1:0));let k=0;
 for(let i=0;i<str.length;i+=4){let a=map[str.charCodeAt(i)],b=map[str.charCodeAt(i+1)],c=map[str.charCodeAt(i+2)],d=map[str.charCodeAt(i+3)];
  i55Assert(a>=0&&b>=0,"Base64 alphabet");out[k++]=(a<<2)|(b>>4);if(str[i+2]!=="="){i55Assert(c>=0,"Base64 c");out[k++]=((b&15)<<4)|(c>>2)}if(str[i+3]!=="="){i55Assert(d>=0,"Base64 d");out[k++]=((c&3)<<6)|d}}
 i55Assert(k===out.length,"Base64 decoded size");return out;
}
function i55Ascii(s){let o=new Uint8Array(s.length);for(let i=0;i<s.length;i++){i55Assert(s.charCodeAt(i)<128,"Non-ASCII payload");o[i]=s.charCodeAt(i)}return o}
function i55Concat(parts,total){let o=new Uint8Array(total),at=0;for(const part of parts){o.set(part,at);at+=part.length}i55Assert(at===total,"Concat size mismatch");return o}
function i55Sha1(data){
 const n=data.length,N=Math.ceil((n+9)/64)*64,a=new Uint8Array(N);a.set(data);a[n]=128;let dv=new DataView(a.buffer);dv.setUint32(N-8,Math.floor(n*8/4294967296));dv.setUint32(N-4,(n*8)>>>0);
 let H=[0x67452301,0xefcdab89,0x98badcfe,0x10325476,0xc3d2e1f0],w=new Int32Array(80);
 for(let off=0;off<N;off+=64){for(let j=0;j<16;j++)w[j]=dv.getInt32(off+4*j,false);
 for(let j=16;j<80;j++){let v=w[j-3]^w[j-8]^w[j-14]^w[j-16];w[j]=(v<<1)|(v>>>31)}
 let [A,B,C,D,E]=H;for(let j=0;j<80;j++){let f,k;if(j<20){f=(B&C)|(~B&D);k=0x5a827999}else if(j<40){f=B^C^D;k=0x6ed9eba1}else if(j<60){f=(B&C)|(B&D)|(C&D);k=0x8f1bbcdc}else{f=B^C^D;k=0xca62c1d6}
 let t=(((A<<5)|(A>>>27))+f+E+k+w[j])|0;E=D;D=C;C=(B<<30)|(B>>>2);B=A;A=t}H=[(H[0]+A)|0,(H[1]+B)|0,(H[2]+C)|0,(H[3]+D)|0,(H[4]+E)|0]}
 return H.map(x=>(x>>>0).toString(16).padStart(8,"0")).join("");
}
function i55GitBlob(raw){const h=i55Ascii(`blob ${raw.length}\0`);return i55Sha1(i55Concat([h,raw],h.length+raw.length))}
const I55_SHA256_K=(()=>{const primes=[];for(let p=2;primes.length<64;p++){let prime=true;for(let v=2;v*v<=p;v++)if(p%v===0){prime=false;break}if(prime)primes.push(p)}return primes.map(p=>Math.floor((Math.cbrt(p)%1)*4294967296)>>>0)})();
const I55_SHA256_H0=(()=>{const primes=[];for(let p=2;primes.length<8;p++){let prime=true;for(let v=2;v*v<=p;v++)if(p%v===0){prime=false;break}if(prime)primes.push(p)}return primes.map(p=>Math.floor((Math.sqrt(p)%1)*4294967296)>>>0)})();
function i55Sha256(data){
 const n=data.length,N=Math.ceil((n+9)/64)*64,b=new Uint8Array(N);b.set(data);b[n]=128;const dv=new DataView(b.buffer);dv.setUint32(N-8,Math.floor(n*8/4294967296));dv.setUint32(N-4,(n*8)>>>0);let H=I55_SHA256_H0.slice(),w=new Uint32Array(64),R=(x,n)=>(x>>>n)|(x<<(32-n));
 for(let at=0;at<N;at+=64){for(let j=0;j<16;j++)w[j]=dv.getUint32(at+4*j,false);for(let j=16;j<64;j++){let s0=R(w[j-15],7)^R(w[j-15],18)^(w[j-15]>>>3),s1=R(w[j-2],17)^R(w[j-2],19)^(w[j-2]>>>10);w[j]=(w[j-16]+s0+w[j-7]+s1)>>>0}
 let[a,c,d,e,f,g,h,z]=H;for(let j=0;j<64;j++){let S1=R(f,6)^R(f,11)^R(f,25),choice=(f&g)^((~f)&h),t1=(z+S1+choice+I55_SHA256_K[j]+w[j])>>>0,S0=R(a,2)^R(a,13)^R(a,22),majority=(a&c)^(a&d)^(c&d),t2=(S0+majority)>>>0;z=h;h=g;g=f;f=(e+t1)>>>0;e=d;d=c;c=a;a=(t1+t2)>>>0}H=[(H[0]+a)>>>0,(H[1]+c)>>>0,(H[2]+d)>>>0,(H[3]+e)>>>0,(H[4]+f)>>>0,(H[5]+g)>>>0,(H[6]+h)>>>0,(H[7]+z)>>>0]}
 return H.map(x=>x.toString(16).padStart(8,"0")).join("");
}
function i55Huffman(lengths){const ct=Array(16).fill(0),table=Array.from({length:16},()=>new Map());for(const x of lengths){i55Assert(x>=0&&x<=15,"Huffman code length");if(x)ct[x]++}let next=Array(16).fill(0),code=0;for(let n=1;n<=15;n++){code=(code+ct[n-1])*2;next[n]=code}for(let i=0;i<lengths.length;i++)if(lengths[i])table[lengths[i]].set(next[lengths[i]]++,i);return table}
const I55_LB=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258];
const I55_LE=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0];
const I55_DB=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577];
const I55_DE=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13];
function i55Inflate(data,size){
 i55Assert(size<=12000000,"NPY member exceeds declared safety ceiling");let ip=0,reg=0,nb=0,k=0,o=new Uint8Array(size);
 function get(n){i55Assert(n>=0&&n<=16,"Invalid bit width");while(nb<n){i55Assert(ip<data.length,"Deflate underflow");reg|=data[ip++]<<nb;nb+=8}let x=reg&((1<<n)-1);reg>>>=n;nb-=n;return x}
 function decode(tab){let v=0;for(let n=1;n<=15;n++){v=(v<<1)|get(1);if(tab[n].has(v))return tab[n].get(v)}throw Error("Invalid Huffman symbol")}
 let last=0;do{last=get(1);let type=get(2);if(type===0){get(nb%8);let len=get(16),inverse=get(16);i55Assert((len^inverse)===65535,"Stored block size mismatch");while(len--){i55Assert(k<size,"Output overrun");o[k++]=get(8)}continue}
 let lit,dist;if(type===1){lit=i55Huffman(Array.from({length:288},(_,i)=>i<144?8:i<256?9:i<280?7:8));dist=i55Huffman(Array(32).fill(5));}
 else if(type===2){const nl=get(5)+257,nd=get(5)+1,nc=get(4)+4,order=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15],cl=Array(19).fill(0);for(let i=0;i<nc;i++)cl[order[i]]=get(3);const ct=i55Huffman(cl),a=[];
 while(a.length<nl+nd){const x=decode(ct);if(x<16)a.push(x);else if(x===16){i55Assert(a.length>0,"Invalid repeated length");let v=a[a.length-1],n=get(2)+3;while(n--)a.push(v)}else if(x===17){let n=get(3)+3;while(n--)a.push(0)}else if(x===18){let n=get(7)+11;while(n--)a.push(0)}i55Assert(a.length<=nl+nd,"Huffman length overrun")}
 lit=i55Huffman(a.slice(0,nl));dist=i55Huffman(a.slice(nl));}
 else throw Error("Reserved deflate type");
 while(true){const x=decode(lit);if(x===256)break;if(x<256){i55Assert(k<size,"Output overrun");o[k++]=x;continue}
 i55Assert(x>=257&&x<=285,"Bad deflate length symbol");const ix=x-257,len=I55_LB[ix]+get(I55_LE[ix]),dx=decode(dist);i55Assert(dx<30,"Bad deflate distance symbol");const back=I55_DB[dx]+get(I55_DE[dx]);i55Assert(back>0&&back<=k,"Invalid deflate backreference");for(let j=0;j<len;j++){i55Assert(k<size,"Output overrun");o[k]=o[k-back];k++}}
 }while(!last);i55Assert(k===size,`Deflate output ${k}/${size}`);return o;
}
function i55Zip(raw){
 i55Assert(raw.length<=25000000,"Oversized NPZ");let dv=new DataView(raw.buffer,raw.byteOffset,raw.byteLength),u16=i=>dv.getUint16(i,true),u32=i=>dv.getUint32(i,true),end=-1;
 for(let i=raw.length-22;i>=Math.max(0,raw.length-65558);i--)if(u32(i)===0x06054b50){end=i;break}
 i55Assert(end>=0,"Missing ZIP end marker");const count=u16(end+10);i55Assert(count===7,"NPZ must have 7 members");let at=u32(end+16),out={};
 for(let k=0;k<count;k++){i55Assert(u32(at)===0x02014b50,"Invalid ZIP central directory");const method=u16(at+10),cs=u32(at+20),size=u32(at+24),nl=u16(at+28),el=u16(at+30),cl=u16(at+32),offset=u32(at+42);
 let name=String.fromCharCode(...raw.slice(at+46,at+46+nl));i55Assert(/^[a-z_]+\.npy$/.test(name)&&!out[name],"Invalid or duplicate NPZ member");i55Assert(u32(offset)===0x04034b50,"Missing ZIP local header");let p=offset+30+u16(offset+26)+u16(offset+28);i55Assert(p+cs<=raw.length,"ZIP data bounds");let comp=raw.subarray(p,p+cs);i55Assert(method===8,"Expected compressed NPZ member");out[name]=i55Inflate(comp,size);at+=46+nl+el+cl;
 }
 const wanted=["x.npy","f.npy","phase.npy","x_star.npy","f_star.npy","reported_evals.npy","documented_max.npy"].sort();i55Assert(Object.keys(out).sort().join("|")===wanted.join("|"),"NPZ schema key mismatch");return out;
}
function i55NPY(raw){
 i55Assert(raw[0]===147&&String.fromCharCode(...raw.slice(1,6))==="NUMPY","Bad NPY signature");const dv=new DataView(raw.buffer,raw.byteOffset,raw.byteLength),at=raw[6]>=2?12:10,hlen=raw[6]>=2?dv.getUint32(8,true):dv.getUint16(8,true);i55Assert(hlen<1024,"Oversized NPY header");
 const head=String.fromCharCode(...raw.slice(at,at+hlen)),mt=/'descr':\s*'([^']+)'/.exec(head),ms=/'shape':\s*\(([^)]*)\)/.exec(head);i55Assert(mt&&ms&&head.includes("'fortran_order': False"),"Unexpected NPY header");
 const dtype=mt[1],shape=ms[1].split(",").map(s=>s.trim()).filter(Boolean).map(Number);i55Assert(shape.length>=1&&shape.length<=2,"NPY shape dimensions");const n=shape.reduce((a,b)=>a*b,1),buf=raw.subarray(at+hlen),width=dtype.endsWith("8")?8:dtype==="|i1"?1:0;
 i55Assert(n>=0&&width*n===buf.length,"NPY byte size and shape");const view=new DataView(buf.buffer,buf.byteOffset,buf.byteLength),vals=[];
 for(let i=0;i<n;i++){if(dtype==="<f8")vals.push(view.getFloat64(i*8,true));else if(dtype==="<i8")vals.push(Number(view.getBigInt64(i*8,true)));else if(dtype==="|i1")vals.push(view.getInt8(i));else throw Error(`Unexpected NPY dtype ${dtype}`)}
 return {vals,shape,dtype,buf};
}
function i55PyRepr(v){
 if(Number.isNaN(v))return "nan";if(v===Infinity)return "inf";if(v===-Infinity)return "-inf";if(Object.is(v,-0))return "-0.0";
 if(v===0)return "0.0";const a=Math.abs(v);let s=String(v);
 if(a>=1e-4&&a<1e16){if(s.includes("e")){const [mant,exp]=s.split("e"),negative=mant[0]==="-",clean=mant.replace("-",""),digits=clean.replace(".",""),dot=clean.includes(".")?clean.indexOf("."):clean.length,place=dot+Number(exp);s=(negative?"-":"")+(place<=0?"0."+"0".repeat(-place)+digits:place>=digits.length?digits+"0".repeat(place-digits.length):digits.slice(0,place)+"."+digits.slice(place))}
 return s.includes(".")?s:s+".0"}
 const parts=v.toExponential().split("e"),ex=Number(parts[1]);return parts[0]+"e"+(ex>=0?"+":"-")+String(Math.abs(ex)).padStart(2,"0");
}
function i55TraceDigest(x,f,phase){const dim=x.shape[1],parts=[];let total=0;
 for(let i=0;i<f.vals.length;i++){let row=x.buf.subarray(i*dim*8,(i+1)*dim*8),value=i55Ascii(i55PyRepr(f.vals[i])),stage=i55Ascii(phase.vals[i]===0?"search":"post");parts.push(row,value,stage);total+=row.length+value.length+stage.length}
 return i55Sha256(i55Concat(parts,total));
}
function i55Flags(x,f,phase,xstar,fstar,repeval,docmax){
 const n=f.vals.length,d=x.shape[1],out={C1:0,C2:0,C3:0,C4:0,C5:0,R1:0,R2:0,R3:0,D2:0},seen=new Set(),matches=[];
 for(let i=0;i<n;i++){const xx=x.vals.slice(i*d,(i+1)*d),key=Array.from(x.buf.subarray(i*d*8,(i+1)*d*8),v=>v.toString(16).padStart(2,"0")).join("");
 if(xx.every(v=>v===-5)||xx.every(v=>v===5))out.C1++;if(seen.has(key))out.C2++;seen.add(key);if(xx.some(v=>v<-5||v>5))out.C3++;if(phase.vals[i]!==0)out.C5++;if(xstar.vals.length===d&&xx.every((v,j)=>Math.abs(v-xstar.vals[j])<=1e-12))matches.push(i)}
 if(docmax.vals[0]>=0)out.C4=Math.max(0,n-docmax.vals[0]);
 if(xstar.vals.length){out.R1=+(matches.length===0);if(Number.isFinite(fstar.vals[0])&&matches.length){const first=f.vals[matches[0]];out.R2=+(Math.abs(fstar.vals[0]-first)>1e-9*Math.max(1,Math.abs(first)))}
 if(Number.isFinite(fstar.vals[0])){const search=f.vals.filter((_,i)=>phase.vals[i]===0);if(search.length){const best=Math.min(...search);out.R3=+(fstar.vals[0]-best>1e-9*Math.max(1,Math.abs(best)))}}}
 if(repeval.vals[0]>=0)out.D2=+(repeval.vals[0]!==n);return out;
}
function i55Objective(fn,coords){
 if(fn==="sphere")return coords.reduce((s,v)=>s+(v+1.3)**2,0);
 if(fn==="rastrigin")return coords.length*10+coords.reduce((s,v)=>s+v*v-10*Math.cos(2*Math.PI*v),0);
 if(fn==="plateau")return coords.reduce((s,v)=>s+Math.floor(v),0);
 throw Error("Invalid frozen function");
}
function i55ArchiveAudit(path,b64,remoteSha,originalEntry,cell){
 i55Assert(path===originalEntry.path,"Source path mismatch");const raw=i55Decode64(b64),gotGit=i55GitBlob(raw);i55Assert(remoteSha===originalEntry.git_blob_sha1&&gotGit===remoteSha,"Original Git blob SHA-1 mismatch");i55Assert(raw.length===originalEntry.size,"Archived binary byte size mismatch");
 const npz=i55Zip(raw),data=Object.fromEntries(Object.entries(npz).map(([k,v])=>[k.slice(0,-4),i55NPY(v)]));
 const library=path.split("/").at(-2),filename=path.split("/").at(-1);const match=/^(sphere|rastrigin|plateau)_(2|10)_(600[0-4])\.npz$/.exec(filename);i55Assert(match!==null,"Unexpected source roster path");const [,fn,dstr,sstr]=match,d=Number(dstr),seed=Number(sstr),n=data.f.vals.length;
 i55Assert(cell&&cell.library===library&&cell.function===fn&&cell.d===d&&cell.seed===seed&&cell.error===null,"Source cell metadata mismatched or failed");
 i55Assert(data.x.dtype==="<f8"&&data.f.dtype==="<f8"&&data.phase.dtype==="|i1","Original NPZ dtype mismatch");i55Assert(data.x.shape.length===2&&data.x.shape[1]===d&&data.x.shape[0]===n&&data.phase.vals.length===n,"Original NPZ x/f/phase shapes mismatch");
 i55Assert(["f_star","reported_evals","documented_max"].every(name=>data[name].vals.length===1),"NPZ result scalar fields");
 const float32=(library==="evox"||library==="evotorch");let checked=0,maxError=0,float64WouldReject=0,rangeViolations=0;
 for(let i=0;i<n;i++){const xx=data.x.vals.slice(i*d,(i+1)*d),arch=data.f.vals[i];i55Assert(xx.every(Number.isFinite)&&Number.isFinite(arch),`Nonfinite original objective cell #${i}`);
 const exact=i55Objective(fn,xx),expected=float32?Math.fround(exact):exact; i55Assert(Number.isFinite(expected),"Nonfinite oracle result");const delta=Math.abs(arch-expected),tol=1e-10*(1+Math.abs(expected));
 i55Assert(delta<=tol,`Frozen objective mismatch: ${path}, row=${i}, diff=${delta} > ${tol}`);maxError=Math.max(maxError,delta);
 if(Math.abs(arch-exact)>1e-10*(1+Math.abs(exact)))float64WouldReject++;
 if(xx.some(v=>v< -5||v>5))rangeViolations++;
 checked++;
 }
 const hash=i55TraceDigest(data.x,data.f,data.phase);i55Assert(hash===cell.hash,`Archived SHA-256 transcript mismatch ${path}: ${hash} vs ${cell.hash}`);i55Assert(n===cell.calls,`Archived calls mismatch ${path}`);
 const gotFlags=i55Flags(data.x,data.f,data.phase,data.x_star,data.f_star,data.reported_evals,data.documented_max);const differing=Object.keys(gotFlags).filter(key=>gotFlags[key]!==cell.flags[key]);i55Assert(differing.length===0,`Detector flags differ ${path}: ${differing.join(",")}`);
 return {path,library,function:fn,d,seed,source_git_blob_sha1:gotGit,source_binary_size:raw.length,
  objective_calls_rechecked:checked,objective_mismatches:0,objective_max_absolute_error:maxError,
  float32_recorder:float32,float64_wrong_policy_rejections:float64WouldReject,
  archived_trace_sha256:cell.hash,recomputed_trace_sha256:hash,trace_sha256_match:true,
  original_flag_counts:gotFlags,recomputed_flags_match:true,
  note:"Archived original A-process only; no A-prime/B replay or optimizer invocation"};
}
async function i55RunConnectorBatch(tools,paths){
 i55Assert(Array.isArray(paths)&&paths.length>0&&paths.length<=8,"Batch supports 1..8 original NPZ paths");
 i55Assert(new Set(paths).size===paths.length,"Duplicate source paths");i55Assert(i55Sha256(i55Ascii("abc"))==="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","SHA-256 self-test failed");
 i55Assert(i55Sha1(i55Ascii("abc"))==="a9993e364706816aba3e25717850c26c9cd0d89d","SHA-1 self-test failed");
 const manifestResponse=(await tools.mcp__GitHub__fetch_file({repository_full_name:I55_REPO,path:I55_MANIFEST})).result;
 i55Assert(manifestResponse.sha===I55_PINNED_MANIFEST_BLOB,"Manifest identity differs from original review");const manifest=JSON.parse(manifestResponse.content);
 i55Assert(manifest.schema==="I65_I55_ORIGINAL_NPZ_GIT_TREE_V1"&&manifest.original_source_commit===I55_ORIGINAL_COMMIT&&manifest.entries.length===620,"Unexpected original source manifest");
 const index=new Map(manifest.entries.map(e=>[e.path,e]));i55Assert(index.size===620,"Duplicate original manifest paths");
 for(const path of paths){i55Assert(index.has(path)&&path.startsWith(I55_BASE),`Not in frozen 620 file roster: ${path}`)}
 const names=[...new Set(paths.map(p=>p.split("/").at(-2)))];
 const sourceCells={};for(const name of names){const res=(await tools.mcp__GitHub__fetch_file({repository_full_name:I55_REPO,path:`research/results/iteration55/cells_${name}.json`,ref:I55_ORIGINAL_COMMIT})).result;
 i55Assert(res.sha===I55_PINNED_CELLS[name],`Frozen metadata blob mismatch: ${name}`);sourceCells[name]=JSON.parse(res.content)}
 const outcome=[];
 for(const path of paths){try{const source=(await tools.mcp__GitHub__fetch_file({repository_full_name:I55_REPO,path,ref:I55_ORIGINAL_COMMIT,encoding:"base64"})).result;
  const m=/^(sphere|rastrigin|plateau)_(2|10)_(600[0-4])\.npz$/.exec(path.split("/").at(-1));const name=path.split("/").at(-2),c=sourceCells[name].cells.find(x=>x.function===m[1]&&x.d===Number(m[2])&&x.seed===Number(m[3]));
  outcome.push({iteration:path,pass:true,...i55ArchiveAudit(path,source.content,source.sha,index.get(path),c)});
 }catch(error){outcome.push({iteration:path,pass:false,error:String(error)})}}
 return {schema:"I65_I55_50_READ_ONLY_ARCHIVAL_REPLAYS_V1",original_commit:I55_ORIGINAL_COMMIT,manifest_blob:I55_PINNED_MANIFEST_BLOB,files_requested:paths.length,
  replayed:outcome.filter(x=>x.pass).length,failed:outcome.filter(x=>!x.pass).length,
  objective_calls:outcome.filter(x=>x.pass).reduce((sum,x)=>sum+x.objective_calls_rechecked,0),
  float32_calls:outcome.filter(x=>x.pass&&x.float32_recorder).reduce((sum,x)=>sum+x.objective_calls_rechecked,0),
  float64_wrong_policy_rejections:outcome.filter(x=>x.pass).reduce((sum,x)=>sum+x.float64_wrong_policy_rejections,0),
  results:outcome,no_new_optimizers:true,full_original_620_replayed:false};
}
if(typeof module!=="undefined"&&module.exports)module.exports={i55RunConnectorBatch,i55ArchiveAudit,i55Sha1,i55Sha256,i55Decode64,i55PyRepr,i55Objective,i55TraceDigest,i55GitBlob,i55Inflate,i55Zip,i55NPY};
