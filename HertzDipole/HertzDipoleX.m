function [Er,Etheta,Ephi] = HertzDipoleX(kr,Theta,Phi,notHuygens)
%returns the field of a Huygens dipole oriented in X. If notHuygens is
%passed as an argument return the field of an electric dipole
[ Er1,Etheta1,Ephi1 ] = F3smn_rThetaPhi( 1,-1,1,kr,Theta,Phi );
[ Er2,Etheta2,Ephi2 ] = F3smn_rThetaPhi( 1,1,1,kr,Theta,Phi );
[ Er3,Etheta3,Ephi3 ] = F3smn_rThetaPhi( 2,-1,1,kr,Theta,Phi );
[ Er4,Etheta4,Ephi4 ] = F3smn_rThetaPhi( 2,1,1,kr,Theta,Phi );

if nargin==3
    Er=conj(-Er1-Er2+Er3-Er4);
    Etheta=conj(-Etheta1-Etheta2+Etheta3-Etheta4);
    Ephi=conj(-Ephi1-Ephi2+Ephi3-Ephi4);
else
    Er=conj(Er3-Er4);
    Etheta=conj(Etheta3-Etheta4);
    Ephi=conj(Ephi3-Ephi4);
end

end

