package consensus;

/**
 * Superclass for BaseEdge and BaseNode.
 * 
 * @author Brian Bushnell
 * @date September 6, 2019
 *
 */
public abstract class BaseGraphPart extends ConsensusObject {
	
	/*--------------------------------------------------------------*/
	/*----------------        Initialization        ----------------*/
	/*--------------------------------------------------------------*/
	
	public BaseGraphPart(int type_){
		type=type_;
		assert(type==REF || type==INS || type==DEL) : type;
	}
	
	/*--------------------------------------------------------------*/
	/*----------------            Methods           ----------------*/
	/*--------------------------------------------------------------*/
	
	/** Name of this type */
	public final String typeString(){
		return TYPE_NAMES[type];
	}

	/** Name of this part */
	public abstract String partString();
	
	/*--------------------------------------------------------------*/
	/*----------------            Fields            ----------------*/
	/*--------------------------------------------------------------*/
	
	/** Type of this part */
	public final int type;
	
}
