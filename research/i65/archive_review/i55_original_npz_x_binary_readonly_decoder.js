/* Original I55 NPZ x.npy read-only byte decoder for GitHub connector base64.
   Independent ECMAScript/DEFLATE path; no Node, library, network or experiment.
   Evaluating this expression returns its pure helper functions. */
(function () {
  "use strict";
  function decodeBase64(s) {
    const alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    const table=new Int16Array(128).fill(-1);
    for (let i=0;i<64;i++) table[alphabet.charCodeAt(i)]=i;
    let bytes=[], buffer=0, width=0;
    for (let k=0;k<s.length;k++) {
      const c=s.charCodeAt(k);
      if (c===61) break;
      if (c>=128||table[c]<0) continue;
      buffer=(buffer<<6)|table[c]; width+=6;
      if (width>=8) { width-=8; bytes.push((buffer>>>width)&255); }
    }
    return new Uint8Array(bytes);
  }
  function inflateRaw(src) {
    let bitBuffer=0,width=0,position=0,output=[];
    const read=n=>{
      while(width<n) {
        if(position>=src.length) throw Error("DEFLATE truncated");
        bitBuffer|=src[position++]<<width; width+=8;
      }
      const result=bitBuffer&((1<<n)-1);
      bitBuffer>>>=n; width-=n;
      return result;
    };
    function huffman(lengths) {
      const counts=new Int32Array(16),next=new Int32Array(16);
      let max=0;
      for(const n of lengths) {
        if(n) { if(n>15)throw Error("Bad Huffman length");counts[n]++;max=Math.max(max,n); }
      }
      let code=0;
      for(let n=1;n<=15;n++) {code=(code+counts[n-1])<<1;next[n]=code;}
      const map=Array.from({length:16},()=>new Map());
      for(let symbol=0;symbol<lengths.length;symbol++) {
        const length=lengths[symbol];
        if(!length)continue;
        let canonical=next[length]++,reverse=0;
        for(let n=0;n<length;n++) {reverse=(reverse<<1)|(canonical&1);canonical>>>=1;}
        map[length].set(reverse,symbol);
      }
      return ()=>{
        let code=0;
        for(let length=1;length<=max;length++) {
          code|=read(1)<<(length-1);
          const symbol=map[length].get(code);
          if(symbol!==undefined)return symbol;
        }
        throw Error("Invalid original DEFLATE Huffman code");
      };
    }
    const lengthBase=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258];
    const lengthExtra=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0];
    const distBase=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577];
    const distExtra=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13];
    let final=0;
    do {
      final=read(1);
      const blockType=read(2);
      if(blockType===0) {
        read(width%8);
        const len=read(16), complement=read(16);
        if(((len^complement)&65535)!==65535)throw Error("Corrupt stored block length");
        for(let i=0;i<len;i++)output.push(read(8));
        continue;
      }
      if(blockType===3)throw Error("Invalid DEFLATE block");
      let literal,distance;
      if(blockType===1) {
        const length=Array.from({length:288},(_,i)=>i<=143?8:i<=255?9:i<=279?7:8);
        literal=huffman(length);
        distance=huffman(Array(32).fill(5));
      } else {
        const nlit=read(5)+257,ndist=read(5)+1,nclen=read(4)+4;
        const order=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15];
        let cl=Array(19).fill(0);
        for(let i=0;i<nclen;i++)cl[order[i]]=read(3);
        const decodeCL=huffman(cl),lengths=[];
        while(lengths.length<nlit+ndist) {
          const symbol=decodeCL();
          if(symbol<=15) lengths.push(symbol);
          else if(symbol===16) {
            if(!lengths.length)throw Error("Invalid repeated Huffman length");
            let count=read(2)+3;
            while(count--)lengths.push(lengths[lengths.length-1]);
          } else {
            let count=symbol===17?read(3)+3:read(7)+11;
            while(count--)lengths.push(0);
          }
          if(lengths.length>nlit+ndist)throw Error("Huffman length overrun");
        }
        literal=huffman(lengths.slice(0,nlit));
        distance=huffman(lengths.slice(nlit));
      }
      while(true) {
        let symbol=literal();
        if(symbol<256) {output.push(symbol);continue;}
        if(symbol===256)break;
        const index=symbol-257;
        if(index<0||index>=lengthBase.length)throw Error("Invalid DEFLATE copy length");
        const len=lengthBase[index]+read(lengthExtra[index]),idx=distance();
        if(idx>=distBase.length)throw Error("Invalid DEFLATE distance");
        const back=distBase[idx]+read(distExtra[idx]);
        if(back<=0||back>output.length)throw Error("Invalid DEFLATE copy distance");
        for(let i=0;i<len;i++)output.push(output[output.length-back]);
      }
    }while(!final);
    return new Uint8Array(output);
  }
  function unpackFirstX(zip) {
    const view=new DataView(zip.buffer,zip.byteOffset,zip.byteLength);
    const u16=p=>view.getUint16(p,true),u32=p=>view.getUint32(p,true);
    if(u32(0)!==0x04034b50||u16(8)!==8)throw Error("Not DEFLATE original NPZ ZIP");
    const nameLength=u16(26),extraLength=u16(28);
    const name=String.fromCharCode(...zip.subarray(30,30+nameLength));
    if(name!=="x.npy")throw Error("NPZ first member is not original x.npy");
    let zipped=u32(18),unzipped=u32(22);
    if(zipped===0xffffffff) {
      const extra=30+nameLength;
      if(u16(extra)!==1)throw Error("Missing NPZ Zip64 size record");
      unzipped=u32(extra+4); zipped=u32(extra+12);
    }
    const offset=30+nameLength+extraLength;
    const raw=inflateRaw(zip.subarray(offset,offset+zipped));
    if(raw.length!==unzipped)throw Error("NPZ x.npy decompression length mismatch");
    return raw;
  }
  function originalSignedCorners(raw,dim,calls) {
    if(raw[0]!==0x93||String.fromCharCode(...raw.subarray(1,6))!=="NUMPY")
      throw Error("Missing original NumPy signature");
    const v=raw[6],start=v===1?10:12;
    if(v!==1&&v!==2)throw Error("Unrecognized NumPy header version");
    const headerLength=v===1?raw[8]+256*raw[9]:
      raw[8]+256*raw[9]+65536*raw[10]+16777216*raw[11];
    const header=String.fromCharCode(...raw.subarray(start,start+headerLength));
    const match=header.match(/'shape':\s*\((\d+),\s*(\d+)\)/);
    if(!match||Number(match[1])!==calls||Number(match[2])!==dim||
      !header.includes("'descr': '<f8'")||!header.includes("'fortran_order': False"))
      throw Error("Original x.npy float64/dimension/call header mismatch");
    const offset=start+headerLength;
    if(raw.length-offset!==dim*calls*8)throw Error("Original x.npy bytes count mismatch");
    const view=new DataView(raw.buffer,raw.byteOffset+offset,raw.length-offset);
    let negative=0,positive=0;
    for(let i=0;i<calls;i++) {
      let neg=true,pos=true;
      for(let j=0;j<dim;j++) {
        const value=view.getFloat64((i*dim+j)*8,true);
        if(value!==-5)neg=false;
        if(value!==5)pos=false;
      }
      if(neg)negative++;
      if(pos)positive++;
    }
    return {negative,positive};
  }
  return {decodeBase64,unpackFirstX,originalSignedCorners};
})()
