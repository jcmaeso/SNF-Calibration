function [  Er,Etheta,Ephi,Ex,Ey ] = dipoleXArray( x,y,z,Ampli,Theta,Phi,kr,notHuygens )
%returns the field of an array Huygens dipole oriented in X. Each dipole is
%weighted by a complex excitation "Ampli". If "notHuygens" is
%passed as an argument return the field of an electric dipole

zo=kr.*cos(Theta);
xo=kr.*sin(Theta).*cos(Phi);
yo=kr.*sin(Theta).*sin(Phi);
Ex=0;
Ey=0;
Ez=0;


for n=1:numel(x)
   
    kri=sqrt((xo-x(n)).^2+(yo-y(n)).^2+(zo-z(n)).^2);
    thetai=acos((zo-z(n))./kri);
    phii=mod(atan2(-(y(n)-yo),-(x(n)-xo)),2*pi);
    
    if nargin==7
        [ Eri,Ethetai,Ephii ] = HertzDipoleX( kri,thetai,phii );
    else
        [ Eri,Ethetai,Ephii ] = HertzDipoleX( kri,thetai,phii,'notHuygens');
    end
    Exi=sin(thetai).*cos(phii).*Eri+cos(thetai).*cos(phii).*Ethetai-sin(phii).*Ephii;
    Eyi=sin(thetai).*sin(phii).*Eri+cos(thetai).*sin(phii).*Ethetai+cos(phii).*Ephii;
    Ezi=cos(thetai).*Eri-sin(thetai).*Ethetai;
    
%   Er=sin(thetai).*cos(phii).*Exi+sin(thetai).*sin(phii).*Eyi+cos(thetai).*Ezi;
%   Etheta=cos(thetai).*cos(phii).*Exi+cos(thetai).*sin(phii).*Eyi-sin(thetai).*Ezi;
%   Ephi=-sin(phii).*Exi+cos(phii).*Eyi;
%   
    Ex=Ex+Exi.*Ampli(n);
    Ey=Ey+Eyi.*Ampli(n);
    Ez=Ez+Ezi.*Ampli(n);
 
end

  Er=sin(Theta).*cos(Phi).*Ex+sin(Theta).*sin(Phi).*Ey+cos(Theta).*Ez;
  Etheta=cos(Theta).*cos(Phi).*Ex+cos(Theta).*sin(Phi).*Ey-sin(Theta).*Ez;
  Ephi=-sin(Phi).*Ex+cos(Phi).*Ey;
 

end


